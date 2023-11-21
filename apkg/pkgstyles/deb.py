"""
apkg package style for **Debian**
and its many clones such as Ubuntu or Mint.

**source template**: content of `debian/` dir (`control`, `changelog`, ...)

**source package:** `*.dsc` + archives

**packages:** `*.deb`

**required distro packages**:

 * core: `devscripts`
 * isolated build: `pbuilder`

**template variables:**

 * `now`: current date in Debian changelog format (RFC 2822)
"""
import email
import email.utils
import glob
import os
from pathlib import Path
import re
import sys
import tempfile

from apkg import ex
from apkg.log import getLogger
from apkg import parse
from apkg import pkgtemplate
from apkg.util.run import cd, run, sudo
from apkg.util.archive import unpack_archive
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


SUPPORTED_DISTROS = [
    "debian",
    "linuxmint",
    "pop",
    "raspbian",
    "ubuntu",
]
DISTRO_REQUIRES = {
    'core': ['build-essential'],
    'isolated': ['pbuilder'],
}


def format_date():
    """
    current date and time in Debian changelog format (RFC 2822)
    """
    return email.utils.formatdate(localtime=True)


TEMPLATE_VARS_DYNAMIC = {
    'now': format_date,
}


RE_PKG_NAME = r'Source:\s*(\S+)'
# orbital regexp cannon to parse Build-Depends from debian/control
RE_BUILD_DEPENDS = (
    r'(?:\n|\A)Build-Depends(?:-Indep)?:[ \t]*'  # no whitespace before
    r'(?:\n[ \t]+)?'  # optional leading newline with whitespace
    r'((?:[^,\n]+)'   # first build dep
    r'(?:,(?:[ \t]*'  # comma separator and optional whitespace
    r'(?:\n[ \t]+)?'  # optional newline starting with whitespace
    r'[^,\n]+))*)'    # 0-N other build deps
)


def is_valid_template(path):
    deb_files = ['rules', 'control', 'changelog']
    return all((path / f).exists() for f in deb_files)


def get_template_name(path):
    control = path / 'control'

    for line in control.open():
        m = re.match(RE_PKG_NAME, line)
        if m:
            return m.group(1)

    raise ex.ParsingFailed(
        msg="unable to determine Source from: %s" % control)


def get_srcpkg_nvr(path):
    nvr, _, _ = str(path.name).rpartition('.')
    return nvr


def copy_pkg_files(src_path, dst_path):
    """
    copy package files at src_path to dst_path

    Find a single *.changes file at src_path
    and copy it and all files it references to dst_path.

    Return a list of all files copied.

    This isn't a part of pkgstyle interface as it's fairly specific to Debian
    """
    changes = list(glob.iglob('%s/*.changes' % (src_path)))
    if not changes:
        raise ex.UnexpectedCommandOutput(
            msg="no *.changes files found when copying package")
    if len(changes) > 1:
        raise ex.UnexpectedCommandOutput(
            msg="multiple *.changes files found when copying package")

    changes_path = Path(changes[0])
    changes_dst_path = dst_path / changes_path.name
    result = []
    shutil.copyfile(changes_path, changes_dst_path)
    result.append(changes_dst_path)

    parser = email.parser.HeaderParser()
    parsed = parser.parsestr(changes_path.read_text())
    for entry in parsed['Files'].split('\n'):
        if not entry:
            # first line is empty
            continue
        items = re.split(r'\s+', entry.strip(), 5)
        if len(items) < 5:
            log.warning("Invalid *.changes line: %s", entry)
            continue
        name = items[4]
        src = src_path / name
        dst = dst_path / name
        shutil.copyfile(src, dst)
        result.append(dst)

    return result


def build_srcpkg(
        build_path,
        out_path,
        archive_paths,
        template,
        tvars):
    """
    build debian source package
    """
    archive_path = archive_paths[0]
    nv, _ = parse.split_archive_ext(archive_path.name)
    log.info("building deb source package: %s", nv)
    log.info("unpacking archive: %s", archive_path)
    source_path = unpack_archive(archive_path, build_path)
    log.verbose("source package root dir: %s", source_path)
    if not source_path or not source_path.exists():
        msg = "archive unpack didn't result in expected dir: %s" % source_path
        raise ex.UnexpectedCommandOutput(msg=msg)
    # render template
    debian_path = source_path / 'debian'
    template.render(debian_path, tvars=tvars)
    # copy archive with debian .orig name
    _, _, _, ext = parse.split_archive_fn(archive_path.name)
    debian_ar = "%s_%s.orig%s" % (tvars['name'], tvars['version'], ext)
    debian_ar_path = build_path / debian_ar
    log.info("copying archive into source package: %s", debian_ar_path)
    shutil.copyfile(archive_path, debian_ar_path)

    log.info("building deb source-only package...")
    with cd(source_path):
        run('dpkg-buildpackage',
            '-S',   # source-only, no binary files
            '-sa',  # source includes orig, always
            '-d',   # do not check build dependencies and conflicts
            '-nc',  # do not pre clean source tree
            '-us',  # unsigned source package.
            '-uc',  # unsigned .changes file.
            )

    log.info("copying source package to result dir: %s", out_path)
    out_path.mkdir(parents=True)
    copied = copy_pkg_files(build_path, out_path)
    dscs = [path for path in copied if path.suffix == '.dsc']
    if not dscs:
        raise ex.UnexpectedCommandOutput(
            msg="no *.dsc files found after source package build")
    return dscs


def build_packages(
        build_path,
        out_path,
        srcpkg_paths,
        **kwargs):
    """
    build .deb packages from source package
    """
    srcpkg_path = srcpkg_paths[0]
    build_path.mkdir(parents=True)
    out_path.mkdir(parents=True)
    isolated = kwargs.get('isolated')
    if isolated:
        log.info("starting isolated build using pbuilder")
        # TODO: ensure pbuilder's base image exists (pbuilder create)
        sudo('pbuilder', 'build',
             '--buildresult', build_path,
             srcpkg_path,
             preserve_env=True,  # preserve env inc. DEB_BUILD_OPTIONS
             )
    else:
        # unpack source package
        log.info("unpacking source package for direct host build")
        srcpkg_abspath = srcpkg_path.resolve()
        with cd(build_path):
            run('dpkg-source', '-x', srcpkg_abspath)
        # find unpacked source dir
        try:
            source_glob = '%s/*/' % build_path
            source_path = Path(glob.glob(source_glob)[0])
        except IndexError:
            msg = "failed to find unpacked source dir: %s"
            raise ex.UnexpectedCommandOutput(msg % source_glob)

        log.info("starting direct host build using dpkg-buildpackage")
        with cd(source_path):
            # build
            run('dpkg-buildpackage',
                '-us',  # unsigned source package.
                '-uc',  # unsigned .changes file.
                )

    log.info("copying built packages to result dir: %s", out_path)
    copied = copy_pkg_files(build_path, out_path)
    pkgs = [path for path in copied if path.suffix in ['.deb', '.ddeb']]
    if not pkgs:
        raise ex.UnexpectedCommandOutput(
            msg="no *.deb packages found after build")
    return pkgs


def install_distro_packages(
        packages,
        **kwargs):
    interactive = kwargs.get('interactive', False)

    cmd = ['apt-get', 'install']
    env = os.environ.copy()
    if not interactive:
        env['DEBIAN_FRONTEND'] = 'noninteractive'
        cmd += ['-y']

    cmd += packages
    sudo(cmd, env=env)


def install_custom_packages(
        packages,
        **kwargs):

    def local_path(pkg):
        """
        apt-get is able to install local packages
        as long as they use full path or relative including ./
        """
        p = str(pkg)
        if p[0] not in '/\\.':
            return "./%s" % p
        return p

    interactive = kwargs.get('interactive', False)

    cmd = ['apt-get', 'install']
    env = os.environ.copy()
    if not interactive:
        env['DEBIAN_FRONTEND'] = 'noninteractive'
        cmd += ['-y']

    cmd += list(map(local_path, packages))
    sudo(cmd, env=env)


def install_build_deps(
        deps,
        **kwargs):
    """
    install debian build deps

    Debian Build-Depends can contain strings not handled by
    `apt-get install` such as "(>= 9~)"

    New `apt-get satisfy` command handles Build-Depends strings fine
    but it isn't available on current.

    Try to use `apt-get satisfy` if available,
    otherwise revert to stripping special strings and use `install`.
    """
    interactive = kwargs.get('interactive', False)

    if has_aptget_satisfy_():
        # unlike install, satisfy can handle versioned deps
        cmd = ['apt-get', 'satisfy']
        env = os.environ.copy()
        if not interactive:
            env['DEBIAN_FRONTEND'] = 'noninteractive'
            cmd += ['-y']
        cmd += deps
        sudo(cmd, env=env)
    else:
        # satisfy not available, strip special strings and use install
        packages = [strip_dep_(d) for d in deps]
        install_distro_packages(packages, **kwargs)


def get_build_deps_from_template(
        template_path,
        **kwargs):
    """
    parse Build-Depends from packaging template
    """
    distro = kwargs.get('distro')
    # render control file
    this_style = sys.modules[__name__]
    t = pkgtemplate.PackageTemplate(template_path, style=this_style)
    tvars = pkgtemplate.DUMMY_VARS.copy()
    if distro:
        tvars['distro'] = distro
    control_text = t.render_file_content('control', tvars=tvars)
    return get_build_deps_from_control_(control_text)


def get_build_deps_from_srcpkg(
        srcpkg_path,
        **_):
    """
    parse Build-Depends from source package
    """
    debar_path = get_srcpkg_debian_archive_(srcpkg_path.parent)
    log.info("unpacking debian archive: %s", debar_path)
    with tempfile.TemporaryDirectory(prefix='apkg_deb_') as td:
        unpack_path = unpack_archive(debar_path, td)
        control_path = unpack_path / 'control'
        control_text = control_path.open().read()
    return get_build_deps_from_control_(control_text)


# functions bellow with _ postfix are specific to this pkgstyle


def get_build_deps_from_control_(control_text):
    """
    parse Build-Depends from debian control file contents
    """
    m = re.findall(RE_BUILD_DEPENDS, control_text)
    if not m:
        msg = "unable to parse Build-Depends from control"
        raise ex.ParsingFailed(msg=msg)
    deps = []
    for deps_raw in m:
        deps += re.split(r'\s*,\s*', deps_raw)
    return deps


def get_srcpkg_debian_archive_(path):
    ars = glob.glob('%s/*.debian.tar.?z' % path)
    if not ars:
        msg = "unable to find debian archive in srcpkg: %s" % path
        raise ex.InvalidInput(msg=msg)
    if len(ars) > 1:
        msg = "multiple debian archives found in srcpkg: %s" % path
        raise ex.InvalidInput(msg=msg)
    return ars[0]


def has_aptget_satisfy_():
    """
    is `apt-get satisfy` command available?
    """
    o = run('apt-get', '-h', check=False, quiet=True)
    return 'satisfy' in o


def strip_dep_(dep):
    """
    strip special version strings (as found in Build-Depends)
    in order for dep to be installable through `apt-get install`
    """
    return re.split(r'[\s\[\(]', dep)[0]
