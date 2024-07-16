import click

from apkg import adistro
from apkg import ex
from apkg.log import getLogger
from apkg import pkgstyle


log = getLogger(__name__)


@click.command(name='system-setup')
@click.option('-c', '--core', is_flag=True,
              help="install core packages for direct package builds  [default]")
@click.option('-I', '--isolated', is_flag=True,
              help="install packages for isolated package builds")
@click.option('-L', '--lint', is_flag=True,
              help="install packages for linting (apkg lint)")
@click.option('-a', '--all', is_flag=True,
              help="install all of above (-cIL)")
@click.option('-d', '--distro',
              help="override target distro  [default: current]")
@click.option('--ask/--no-ask', 'interactive',
              default=False, show_default=True,
              help="enable/disable interactive mode")
@click.help_option('-h', '--help',
                   help="show this help message")
def cli_system_setup(*args, **kwargs):
    """
    setup system for packaging

    Install native distro packages required for packaging.

    Select desired packages with a combination of

    -c / --core: core packages for direct package builds  [default]

    -I / --isolated`: packages for isolated package builds

    -L / --lint`: packages for linting (apkg lint)

    or

    -a / --all to select all above.

    Defaults to --core when no options are supplied.
    """
    return system_setup(*args, **kwargs)


def system_setup(
        core=False,
        isolated=False,
        lint=False,
        all=False,
        distro=None,
        interactive=False):
    """
    setup system for packaging
    """
    cats_opts = {
        'core': core,
        'isolated': isolated,
        'lint': lint,
    }
    if all:
        # install all categories
        cats = cats_opts.keys()
    else:
        # nstall only selected categories
        cats = [cat for cat, e in cats_opts.items() if e]
        if not cats:
            # default to --core
            cats = ['core']

    cats_txt = ", ".join(cats)
    log.bold("system setup: %s", cats_txt)

    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)

    style = pkgstyle.get_pkgstyle_for_distro(distro)
    if not style:
        raise ex.DistroNotSupported(distro=distro)
    log.info("target pkgstyle: %s", style.name)

    distro_reqs = getattr(style, 'DISTRO_REQUIRES', {})
    reqs = []
    for cat in cats:
        reqs += distro_reqs.get(cat, [])

    if reqs:
        pkgstyle.call_pkgstyle_fun(
            style, 'install_distro_packages',
            reqs,
            distro=distro,
            interactive=interactive)
    else:
        log.info("no distro packages required")

    log.success("system setup successful: %s", cats_txt)


APKG_CLI_COMMANDS = [cli_system_setup]
