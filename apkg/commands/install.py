import click

from apkg import adistro
from apkg.commands.build import build
from apkg import ex
from apkg.log import getLogger
from apkg import pkgstyle
from apkg.util import common


log = getLogger(__name__)


@click.command(name="install")
@click.argument('inputs', nargs=-1)
@click.option('-C', '--custom-pkgs', is_flag=True,
              help="install custom packages (no build)")
@click.option('-D', '--distro-pkgs', is_flag=True,
              help="install packages from distro repos (no build)")
@click.option('-s', '--srcpkg', is_flag=True,
              help="build and install packages from srcpkg")
@click.option('-a', '--archive', is_flag=True,
              help="build and install packages from archive")
@click.option('-u', '--upstream', is_flag=True,
              help="build and install upstream packages")
@click.option('-v', '--version',
              help=("upstream archive version to use"
                    ", implies --upstream"))
@click.option('-r', '--release',
              help="set release for built packages  [default: 1]")
@click.option('-b', '--build-dep', is_flag=True,
              help="install build deps on host (apkg build-dep)")
@click.option('-d', '--distro',
              help="override target distro  [default: current]")
@click.option('--reinstall', is_flag=True,
              help="[!] reinstall existing packages")
@click.option('--force', is_flag=True,
              help="[!] allow dangerous operations (downgrade, erase, replace)")
@click.option('--cache/--no-cache', default=True, show_default=True,
              help="enable/disable cache")
@click.option('--ask/--no-ask', 'interactive',
              default=False, show_default=True,
              help="enable/disable interactive mode")
@click.option('-F', '--in-file', 'in_files', multiple=True,
              help="specify input file, '-' to read from stdin")
@click.option('-y', '--yes', 'interactive', flag_value=False, hidden=True,
              help="[DEPRECATED] compat alias for --no-ask")
@click.help_option('-h', '--help',
                   help="show this help message")
def cli_install(*args, **kwargs):
    """
    install packages using native package manager

    Default: build packages and install them

    `apkg build` options are available

    you can supply a list of --custom-pkgs or --distro-pkgs to install
    specified custom/distro packages directly without any build
    """
    return install(*args, **kwargs)


def install(
        custom_pkgs=False,
        distro_pkgs=False,
        srcpkg=False,
        archive=False,
        upstream=False,
        inputs=None,
        in_files=None,
        version=None,
        release=None,
        distro=None,
        build_dep=False,
        reinstall=False,
        force=False,
        cache=True,
        interactive=False):
    """
    install packages using native package manager
    """
    log.bold("installing packages")

    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)

    ps = pkgstyle.get_pkgstyle_for_distro(distro)
    if not ps:
        raise ex.DistroNotSupported(distro=distro)
    log.info("target pkgstyle: %s", ps.name)

    inputs = common.parse_inputs(inputs, in_files)

    pkgs = []
    result = None

    if custom_pkgs:
        if distro_pkgs:
            raise ex.InvalidInput(
                fail=("--custom-pkgs and --distro-pkgs options"
                      " are mutually exclusive"))

        pkgs = inputs
        result = pkgstyle.call_pkgstyle_fun(
            ps, 'install_custom_packages',
            pkgs,
            distro=distro,
            reinstall=reinstall,
            force=force,
            interactive=interactive)
    elif distro_pkgs:
        pkgs = inputs
        result = pkgstyle.call_pkgstyle_fun(
            ps, 'install_distro_packages',
            pkgs,
            distro=distro,
            reinstall=reinstall,
            force=force,
            interactive=interactive)
    else:
        # default: use build to get packages
        pkgs = build(
            srcpkg=srcpkg,
            archive=archive,
            upstream=upstream,
            inputs=inputs,
            version=version,
            release=release,
            distro=distro,
            build_dep=build_dep,
            cache=cache)

        result = pkgstyle.call_pkgstyle_fun(
            ps, 'install_custom_packages',
            pkgs,
            distro=distro,
            reinstall=reinstall,
            force=force,
            interactive=interactive)

    log.success("installed %s packages", len(pkgs))

    return result


APKG_CLI_COMMANDS = [cli_install]
