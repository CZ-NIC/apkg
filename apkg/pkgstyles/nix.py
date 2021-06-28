"""
apkg package style for **Nix** (NixOS.org).

**source template:**
 - `default.nix` as-if in https://github.com/NixOS/nixpkgs
 - `top-level.nix` that simply wraps it to be buildable outside the official tree,
   in particular it should substitute the source archive;
   e.g. see ../../distro/pkg/nix/top-level.nix

**source package:** the same, just with templates substituted

**packages:** symlink to your local nix store (for the primary package output)
"""
import hashlib
import os
import re

from apkg import ex
from apkg.log import getLogger
from apkg.util.run import run
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


SUPPORTED_DISTROS = [
    'nix'
]

def fname_(path):
    return path / "default.nix"

def is_valid_template(path):
    return (path / "default.nix").exists() and (path / "top-level.nix").exists()

def get_template_name(path):
    # I'd like to simply use nix directly, e.g.:
    #   return run("nix", "eval", "--file", path / "top-level.nix", "pname", "--raw")
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

# https://stackoverflow.com/a/44873382/587396
def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def build_srcpkg(
        build_path,
        out_path,
        archive_paths,
        template,
        env):
    archive_path = archive_paths[0]
    env = env or {}
    env['src_hash'] = sha256sum(archive_path)
    out_archive = out_path / archive_path.name
    log.info("applying templates")
    template.render(build_path, env or {})
    log.info("copying everything to: %s", out_path)
    shutil.copytree(build_path, out_path)
    shutil.copyfile(archive_path, out_archive)
    return [out_path / 'top-level.nix', out_path / 'default.nix', out_archive]
    # TODO: maybe list everything in the directory?  (e.g. local patches might be there)

def build_packages(
        build_path,
        out_path,
        srcpkg_paths,
        **_):
    log.info("building using nix (silent unless fail)") # TODO: perhaps without -L and shown?
    run('nix', 'build', '--file' , srcpkg_paths[0], '--out-link', out_path / 'result',
            '--print-build-logs', # get full logs shown on failure
            '--keep-failed', # and keep the nix build dir for inspection
        )
    return list(out_path.glob('result*'))

def install_custom_packages(
        packages,
        **kwargs):

    cmd = ['nix-env', '--install']

    dry_run = kwargs.get('interactive', False) # there's no real "interactive" mode
    if dry_run:
        cmd += ['--dry-run']

    if not len(packages) > 0: # otherwise it might try installing everything :-)
        raise ex.InvalidInput(msg="no packages to install")
    # We don't check that `packages` are really custom packages;
    # they could be parameters, distro package names, etc.
    cmd += packages

    run(*cmd, env=os.environ.copy(), direct=True)

