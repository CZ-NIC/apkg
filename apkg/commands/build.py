"""
build packages

Usage: apkg build [-u] [-s <srcpkg> | -a <ar>]
                  [-v <ver>] [-r <rls>] [-d <distro>]
                  [-O <dir>]
                  [-H] [-i] [--no-cache]

Options:
  -u, --upstream                  upstream build from archive
                                  default: dev build from project
  -s <srcpkg>, --srcpkg <srcpkg>  use specified source package (path or name)
  -a <ar>, --archive <ar>         use specified archive (path or name)
  -v <ver>, --version <ver>       set package version
  -r <rls>, --release <rls>       set package release
  -d <distro>, --distro <distro>  set target distro
                                  default: current distro
  -O <dir>, --result-dir <dir>    put results into specified dir
                                  default: pkg/pkgs/DISTRO/NVR
  -H, --host-build                build directly on host (!) without isolated env
                                  default: use isolated builder (pbuilder, mock, ...)
  -i, --install-dep               install build dependencies on host
                                  only works with -H/--host-build
  --no-cache                      disable cache
""" # noqa

from docopt import docopt

from apkg.lib import build
from apkg.lib import common


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    results = build.build_package(
        srcpkg=args['--srcpkg'],
        archive=args['--archive'],
        upstream=args['--upstream'],
        version=args['--version'],
        release=args['--release'],
        distro=args['--distro'],
        result_dir=args['--result-dir'],
        install_dep=args['--install-dep'],
        isolated=not args['--host-build'],
        use_cache=not args['--no-cache'])
    common.print_results(results)
    return results
