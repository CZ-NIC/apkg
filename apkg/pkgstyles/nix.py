"""
apkg package style for **Nix** ([NixOS.org](https://nixos.org)).

**source template:**

- `default.nix` as-if in [https://github.com/NixOS/nixpkgs](https://github.com/NixOS/nixpkgs)
- `top-level.nix` that simply wraps it to work outside that official tree,
   in particular it should substitute the source archive;
   e.g. see `apkg/distro/pkg/nix/top-level.nix`

**source package:** the same, just with templates substituted

**packages:** symlink to your local nix store (for the primary package output)
"""
import os
import re

from apkg import ex
from apkg.log import getLogger
from apkg.util.run import run
import apkg.util.shutil35 as shutil
from apkg.util.common import hash_file

log = getLogger(__name__)


SUPPORTED_DISTROS = [
    'nix',
    'nixos',
]


def fname_(path):
    return path / "default.nix"


def is_valid_template(path):
    return ((path / "default.nix").exists()
            and (path / "top-level.nix").exists())


def get_template_name(path):
    # I'd like to simply use nix directly, e.g.:
    #   return run("nix", "eval", "--file", path / "top-level.nix",
    #           "pname", "--raw")
    # but that would require substituting the templates first.
    # So we use a hacky regexp instead :-/
    expr = fname_(path)
    for line in expr.open():
        m = re.match(r'\s*pname\s*=\s*"(\S+)";', line)
        if m:
            return m.group(1)
    raise ex.ParsingFailed(
        msg="unable to determine Name from: %s" % expr)


def get_srcpkg_nvr(path):
    # use source package parent dir as NVR
    return path.resolve().parent.name


def get_build_deps_from_template(  # pylint: disable=unused-argument
        template_path,
        **kwargs):
    # With nix it doesn't make so much sense to care about build deps.
    return []


def install_build_deps(  # pylint: disable=unused-argument
        deps,
        **kwargs):
    return


def build_srcpkg(
        build_path,
        out_path,
        archive_paths,
        template,
        tvars):
    archive_path = archive_paths[0]
    tvars = tvars or {}
    tvars['src_hash'] = hash_file(archive_path).hexdigest()
    out_archive = out_path / archive_path.name
    log.info("applying templates")
    template.render(build_path, tvars=tvars)
    log.info("copying everything to: %s", out_path)
    shutil.copytree(build_path, out_path)
    shutil.copyfile(archive_path, out_archive)
    return [out_path / 'top-level.nix', out_path / 'default.nix', out_archive]
    # TODO: maybe list everything in the directory?
    #       (e.g. local patches might be there)


def build_packages(
        build_path,  # pylint: disable=unused-argument
        out_path,
        srcpkg_paths,
        **_):
    log.info("building using nix (silent unless fail)")
    # TODO: use "nix" command CLI after versions < 2.4 get less common
    # (because `--extra-experimental-features nix-command` support).
    # That new CLI is officially experimental (up to change),
    # but we'd be using it in way that seem extremely unlikely to break.
    # The reason is that its output will be a bit more user-friendly.
    # Perhaps use it without --print-build-logs and shown? (has color status)
    run('nix-build', srcpkg_paths[0],
        '--out-link', out_path / 'result',
        '--keep-failed',  # and keep the nix build dir for inspection
        )
    return list(out_path.glob('result*'))


def install_custom_packages(
        packages,
        **kwargs):

    cmd = ['nix-env', '--install']

    # There's no real "interactive" mode.
    dry_run = kwargs.get('interactive', False)
    if dry_run:
        cmd += ['--dry-run']

    if not len(packages) > 0:  # otherwise it tries installing everything :-)
        raise ex.InvalidInput(msg="no packages to install")
    # We don't check that `packages` are really custom packages;
    # they could be parameters, distro package names, etc.
    cmd += packages

    run(cmd, env=os.environ.copy())
