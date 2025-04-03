"""
apkg package style for RPM-based distros
such as Fedora, CentOS, SUSE, RHEL.

**source template**: `*.spec` and friends

**source package:** `*.src.rpm`

**packages:** `*.rpm`

**required distro packages**:

 * core: `rpm-build`
 * isolated build: `mock`

**template variables:**

 * `now`: current date in RPM changelog format
"""
from datetime import datetime
import glob
from pathlib import Path
import re
import subprocess

from packaging.version import Version

from apkg import ex
from apkg.util import common
from apkg.log import getLogger
from apkg.util.run import run, sudo
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


EL_FAMILY_DISTROS = [
    "almalinux",
    "centos",
    "oracle",
    "rhel",
    "rocky",
    "scientific",
]
SUPPORTED_DISTROS = sorted(EL_FAMILY_DISTROS + [
    "fedora",
    "opensuse",
    "pidora",
])
DISTRO_REQUIRES = {
    'core': ['rpm-build'],
    'isolated': ['mock'],
    'lint': ['rpmlint'],
}


def format_date():
    """
    current date and time in RPM changelog format
    """
    return datetime.now().strftime('%a %b %d %Y')


TEMPLATE_VARS_DYNAMIC = {
    'now': format_date,
}


RE_PKG_NAME = r'Name:\s*(\S+)'
RE_BUILD_REQUIRES = r'BuildRequires:\s*(.*)'
RE_RPMBUILD_OUT_RPM = r'Wrote:\s+(.*\.rpm)\s*'
RE_RPMBUILD_OUT_SRPM = r'Wrote:\s+(.*\.src.rpm)\s*'


def is_valid_template(path):
    return bool(get_spec_(path))


def get_template_name(template, distro=None):
    """
    get Name from .spec
    """
    spec_text = render_spec_from_template_(template, distro=distro)
    for line in spec_text.splitlines():
        m = re.match(RE_PKG_NAME, line)
        if m:
            name = m.group(1)
            if has_rpm_macros_(name):
                raise ex.ParsingFailed(
                    msg="unable to parse RPM macro in Name: %s" % name)
            return name

    raise ex.ParsingFailed(
        msg="unable to determine Name from rpm template: %s" % template.path)


def get_srcpkg_nvr(path):
    name = str(path.name)
    m = re.match(r'(.*)\.src.rpm', name)
    if m:
        return m.group(1)
    return name


def build_srcpkg(
        build_path,
        out_path,
        archive_info,
        template,
        tvars):
    """
    build .src.rpm source package
    """
    rpmbuild_topdir = build_path / 'rpmbuild'
    rpmbuild_src = rpmbuild_topdir / 'SOURCES'
    rpmbuild_spec = rpmbuild_topdir / 'SPEC'

    rpmbuild_src.mkdir(parents=True, exist_ok=True)

    template.render(rpmbuild_src, tvars=tvars)

    spec_src_path = get_spec_(rpmbuild_src)
    spec_path = rpmbuild_spec / spec_src_path.name
    log.verbose("moving .spec file into SPEC: %s", spec_path)
    rpmbuild_spec.mkdir(exist_ok=True)
    spec_src_path.rename(spec_path)

    log.info("copying archive files into SOURCES: %s", rpmbuild_src)
    archive_paths = [archive_info["archive"]]
    archive_paths.extend(archive_info.get("components", {}).values())
    for src_path in archive_paths:
        dst_path = rpmbuild_src / src_path.name
        shutil.copyfile(src_path, dst_path)
    log.info("building .src.rpm using rpmbuild")
    out = run('rpmbuild', '-bs',
              '--define', '_topdir %s' % rpmbuild_topdir.resolve(),
              spec_path)

    log.info("copying .src.rpm to result dir: %s", out_path)
    out_path.mkdir(parents=True)
    srcpkgs = []
    for m in re.finditer(RE_RPMBUILD_OUT_SRPM, out):
        srpm = m.group(1)
        src_srpm = Path(srpm)
        dst_srpm = out_path / src_srpm.name
        shutil.copyfile(src_srpm, dst_srpm)
        srcpkgs.append(dst_srpm)
    if not srcpkgs:
        raise ex.ParsingFailed(
            msg="unable to parse rpmbuild results")
    if len(srcpkgs) > 1:
        raise ex.UnexpectedCommandOutput(
            msg="rpmbuild produced multiple .src.rpm files")
    return srcpkgs


def build_packages(
        build_path,
        out_path,
        srcpkg_paths,
        **kwargs):
    """
    build .rpm packages from .src.rpm
    """
    isolated = kwargs.get('isolated')
    pkgs = []
    srcpkg_path = srcpkg_paths[0]

    if isolated:
        log.info("starting isolated .rpm build using mock")
        # sudo shouldn't be necessary when in mock group
        # but apkg can't rely on that especially in containers etc.
        sudo('mock',
             '--resultdir', build_path,
             srcpkg_path,
             preserve_env=True)
        log.info("copying built packages to result dir: %s", out_path)
        out_path.mkdir(parents=True)
        for rpm in glob.iglob('%s/*.rpm' % build_path):
            src_pkg = Path(rpm)
            dst_pkg = out_path / src_pkg.name
            shutil.copyfile(src_pkg, dst_pkg)
            pkgs.append(dst_pkg)
    else:
        log.info("starting direct host .rpm build using rpmbuild")
        rpmbuild_topdir = build_path / 'rpmbuild'
        rpmbuild_topdir.mkdir(parents=True, exist_ok=True)
        out = run('rpmbuild', '--rebuild',
                  '--define', '_topdir %s' % rpmbuild_topdir.resolve(),
                  srcpkg_path)
        log.info("copying built packages to result dir: %s", out_path)
        out_path.mkdir(parents=True)
        for m in re.finditer(RE_RPMBUILD_OUT_RPM, out):
            rpm = m.group(1)
            src_pkg = Path(rpm)
            dst_pkg = out_path / src_pkg.name
            shutil.copyfile(src_pkg, dst_pkg)
            pkgs.append(dst_pkg)
        if not pkgs:
            raise ex.ParsingFailed(
                msg="unable to parse rpmbuild results")

    return pkgs


def install_build_deps(
        deps,
        **kwargs):
    # dnf/zypper install handles build deps
    install_distro_packages(deps, **kwargs)


def install_custom_packages(
        packages,
        **kwargs):
    # dnf/zypper install handles local packages
    kwargs['allow_unsigned'] = True
    install_distro_packages(packages, **kwargs)


def install_distro_packages(
        packages,
        **kwargs):
    allow_unsigned = kwargs.get('allow_unsigned', False)
    interactive = kwargs.get('interactive', False)
    distro = kwargs.get('distro')
    reinstall = kwargs.get('reinstall', False)
    force = kwargs.get('force', False)
    pm = get_package_manager_(distro)

    cmd = [pm]
    if pm == 'zypper':
        # zypper (openSUSE)
        cmd += ['install']
        if reinstall or force:
            # exclusive with -C
            cmd += ['--force']
        else:
            # use zypper capabilities
            cmd += ['-C']
        if force:
            cmd += ['--replacefiles']
        if allow_unsigned:
            cmd += ['--allow-unsigned-rpm']
    else:
        # dnf (Fedora / EL)
        if reinstall:
            cmd += ['reinstall']
        else:
            cmd += ['install']
        if force:
            cmd += ['--allowerasing']

    if not interactive:
        cmd += ['-y']
    cmd += packages
    sudo(cmd)


def get_build_deps_from_template(
        template,
        distro=None):
    """
    parse BuildRequires from packaging template
    """
    spec_text = render_spec_from_template_(template, distro=distro)
    return get_build_deps_from_spec_(spec_text)


def get_build_deps_from_srcpkg(
        srcpkg_path,
        **_):
    """
    parse BuildRequires from .src.rpm
    """
    cmd = "rpm2cpio '%s' | cpio -i --to-stdout '*.spec'" % srcpkg_path
    spec_text = subprocess.getoutput(cmd)
    return get_build_deps_from_spec_(spec_text)


def lint(
        pkg_paths,
        info=False,
        strict=False,
        distro=None,
        **kwargs):
    """
    lint files using rpmlint
    """
    log.info('linting %s files with rpmlint', len(pkg_paths))
    suse = distro and distro.id == 'opensuse'
    cmd = ['rpmlint']
    if info:
        cmd += ['--info']
    if strict and not suse:
        cmd += ['--strict']
    cmd += pkg_paths
    o = run(cmd, check=False, direct=True)
    return o.returncode


# functions bellow with _ postfix are specific to this pkgstyle


def get_package_manager_(distro):
    default = 'dnf'
    if not distro:
        return default
    if distro.id == 'opensuse':
        return 'zypper'
    if (distro.id in EL_FAMILY_DISTROS
            and distro.version
            and Version(distro.version) <= Version("7")):
        # use yum on EL <= 7
        return 'yum'
    return default


def get_spec_(path):
    for s in glob.iglob("%s/*.spec" % path):
        return Path(s)
    return None


def render_spec_from_template_(template, distro=None, parse_macros=True):
    """
    render spec file from template
    """
    spec_path = get_spec_(template.path).relative_to(template.path)
    tvars = {}
    if distro:
        tvars['distro'] = distro
    spec_txt = template.render_file_content(spec_path, tvars=tvars)
    if parse_macros:
        spec_txt = parse_spec_(spec_txt)
    return spec_txt


def parse_spec_(spec_text):
    """
    parse spec to expand macros if rpmbuild is available
    """
    # done through temp file because rpmspec doesn't work
    # on /dev/stdin on openSUSE for some reason :-/
    with common.text_tempfile(spec_text, prefix='apkg_rpm.spec_') as spec_path:
        try:
            spec_parsed = run('rpmspec', '-P', spec_path, quiet=True)
        except ex.CommandNotFound:
            log.warning("rpmspec not available - unable to parse RPM macros in .spec")
            log.info("consider running `apkg system-setup` to get rpmspec"
                     " or installing rpm-build package manually")
            return spec_text

    return spec_parsed


def get_build_deps_from_spec_(spec_text):
    """
    parse BuildRequires from .spec file content
    """
    return re.findall(RE_BUILD_REQUIRES, spec_text)


def has_rpm_macros_(s):
    """
    does string contain RPM macros? (patterns like %{name} or %name)
    """
    return bool(re.search(r'%\{?\w+\}?', s))
