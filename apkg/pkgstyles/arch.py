"""
apkg package style for **Arch** linux.

**source template:** `PKGBUILD`

**source package:** `PKGBUILD`

**packages:** `*.zst`
"""
import glob
from pathlib import Path
import shutil

from apkg import ex
from apkg.log import getLogger
from apkg.util.run import cd, run, sudo


log = getLogger(__name__)


SUPPORTED_DISTROS = [
    'arch',
    'manjaro',
]
DISTRO_REQUIRES = {
    'core': ['base-devel'],
}


RE_PKG_NAME = r'pkgname\s*=\s*(\S+)'


def is_valid_template(path):
    pkgbuild = path / "PKGBUILD"
    return pkgbuild.exists()


def get_template_name(template, distro=None):
    pkgbuild_text = render_pkgbuild_from_template_(template, distro=distro)
    return parse_pkgbuild_content_(pkgbuild_text, 'echo "$pkgname"')


def get_srcpkg_nvr(path):
    return parse_pkgbuild_(path, 'echo "$pkgname-$pkgver-$pkgrel"')


def build_srcpkg(
        build_path,
        out_path,
        archive_info,
        template,
        tvars):
    archive_path = archive_info['archive']
    in_pkgbuild = build_path / 'PKGBUILD'
    out_pkgbuild = out_path / 'PKGBUILD'
    out_archive = out_path / archive_path.name
    log.info("building arch source package: %s", in_pkgbuild)
    template.render(build_path, tvars or {})
    out_path.mkdir(parents=True)

    log.info("copying PKGBUILD and archive to: %s", out_path)
    shutil.copyfile(in_pkgbuild, out_pkgbuild)
    archive_paths = [archive_info["archive"]]
    archive_paths.extend(archive_info.get("components", {}).values())
    for src_path in archive_paths:
        dst_path = out_path / src_path.name
        shutil.copyfile(src_path, dst_path)

    return [out_pkgbuild, out_archive]


def build_packages(
        build_path,
        out_path,
        srcpkg_paths,
        **_):
    srcpkg_path = srcpkg_paths[0]
    if srcpkg_path.name != 'PKGBUILD':
        raise ex.InvalidSourcePackageFormat(
            fmt="arch source package format is PKGBUILD but got: %s"
            % srcpkg_path.name)
    log.info("copying source package to build dir: %s", build_path)
    shutil.copytree(srcpkg_path.parent, build_path)
    # build package using makepkg
    log.info("starting arch package build using makepkg")
    with cd(build_path):
        run('makepkg')
    log.info("copying built packages to result dir: %s", out_path)
    out_path.mkdir(parents=True, exist_ok=True)
    pkgs = []
    # find and copy resulting packages
    for src_pkg in glob.iglob('%s/*.zst' % build_path):
        dst_pkg = out_path / Path(src_pkg).name
        shutil.copyfile(src_pkg, dst_pkg)
        pkgs.append(dst_pkg)

    return pkgs


def install_distro_packages(
        packages,
        **kwargs):
    interactive = kwargs.get('interactive', False)
    cmd = ['pacman', '-S', '--needed']
    if not interactive:
        cmd += ['--noconfirm']
    cmd += packages
    sudo(cmd)


def install_custom_packages(
        packages,
        **kwargs):
    interactive = kwargs.get('interactive', False)
    cmd = ['pacman', '-U']
    if not interactive:
        cmd += ['--noconfirm']
    cmd += packages
    sudo(cmd)


def install_build_deps(
        deps,
        **kwargs):
    # no special handling for build deps on arch
    install_distro_packages(deps, **kwargs)


def get_build_deps_from_template(
        template,
        distro=None):
    """
    parse depends and makedepends from packaging template
    """
    # render PKGBUILD
    pkgbuild_text = render_pkgbuild_from_template_(template, distro=distro)
    # depends: required for build and run
    depends = parse_pkgbuild_content_(
        pkgbuild_text,
        'printf \'%s\n\' "${depends[@]}"').splitlines()
    # makedepends: required for build only
    makedepends = parse_pkgbuild_content_(
        pkgbuild_text,
        'printf \'%s\n\' "${makedepends[@]}"').splitlines()
    return depends + makedepends


def render_pkgbuild_from_template_(template, distro=None):
    """
    render PKGBUILD file from template
    """
    tvars = {}
    if distro:
        tvars['distro'] = distro
    pkgbuild_txt = template.render_file_content('PKGBUILD', tvars=tvars)
    return pkgbuild_txt


def get_build_deps_from_srcpkg(
        srcpkg_path,
        **_):
    """
    parse depends from source package (PKGBUILD)
    """
    deps = parse_pkgbuild_(
        srcpkg_path,
        'printf \'%s\n\' "${depends[@]}"')
    return deps.splitlines()


# functions bellow with _ postfix are specific to this pkgstyle


def parse_pkgbuild_(pkgbuild, bash):
    return run('bash', '-c', '. "%s" && %s'
               % (pkgbuild, bash), quiet=True)


def parse_pkgbuild_content_(pkgbuild_text, bash):
    pkgb = '%s\n%s' % (pkgbuild_text, bash)
    return run('bash', '-s', input=pkgb, quiet=True)
