import click

from apkg import adistro
from apkg import ex
from apkg.log import getLogger
from apkg import pkgstyle


log = getLogger(__name__)


@click.command(name='system-setup')
@click.option('-I', '--isolated', is_flag=True,
              help="also install packages for isolated build")
@click.option('-d', '--distro',
              help="override target distro  [default: current]")
@click.option('--ask/--no-ask', 'interactive',
              default=False, show_default=True,
              help="enable/disable interactive mode")
def cli_system_setup(*args, **kwargs):
    """
    setup system for packaging
    """
    return system_setup(*args, **kwargs)


def system_setup(
        isolated=False,
        distro=None,
        interactive=False):
    """
    setup system for packaging

    Install native distro packages required for packaging.
    """
    log.bold("system setup for packaging")

    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)

    style = pkgstyle.get_pkgstyle_for_distro(distro)
    if not style:
        raise ex.DistroNotSupported(distro=distro)
    log.info("target pkgstyle: %s", style.name)

    distro_reqs = getattr(style, 'DISTRO_REQUIRES', {})
    reqs = distro_reqs.get('core', [])
    if isolated:
        reqs += distro_reqs.get('isolated', [])
    if reqs:
        pkgstyle.call_pkgstyle_fun(
            style, 'install_distro_packages',
            reqs,
            distro=distro,
            interactive=interactive)
    else:
        log.info("no distro packages required")

    log.success("system ready for packaging")


APKG_CLI_COMMANDS = [cli_system_setup]
