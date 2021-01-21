"""
build package

usage: apkg build ([-u] | [-s <srcpkg>] | [-a <ar>] )
                  [-v <ver>] [-r <rls>] [-d <distro>]
                  [-i] [-I]

options:
  -s <srcpkg>, --srcpkg <srcpkg>  use specified source package (path or name)
  -a <ar>, --archive <ar>         use specified archive (path or name)
  -u, --upstream                  use upstream archive / apkg get-source
                                  default: use dev archvie / apkg make-source
  -v <ver>, --version <ver>       set package version
  -r <rls>, --release <rls>       set package release
  -d <distro>, --distro <distro>  set target distro
                                  default: current distro
  -i, --install-dep               install build dependencies
  -I, --isolated                  use isolated builder (pbuilder/mock) if supported
                                  default: use direct build
""" # noqa

from docopt import docopt

from apkg.lib import build


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    pkgs = build.build_package(
            srcpkg=args['--srcpkg'],
            archive=args['--archive'],
            upstream=args['--upstream'],
            version=args['--version'],
            release=args['--release'],
            distro=args['--distro'],
            install_dep=args['--install-dep'],
            isolated=args['--isolated'])
    for pkg in pkgs:
        print("%s" % pkg)
    return pkgs
