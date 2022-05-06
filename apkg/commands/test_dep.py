import click

from apkg import adistro
from apkg.cli import cli
from apkg.pkgstyle import call_pkgstyle_fun, get_pkgstyle_for_distro
from apkg.commands.get_archive import parse_archive_args
from apkg.util import common
from apkg.log import getLogger
from apkg.project import Project


log = getLogger(__name__)


@cli.command(name="test-dep", aliases=['testdep'])
@click.argument('input_files', nargs=-1)
@click.option('-l', '--list', 'install', default=True, flag_value=False,
              help="list test deps only, don't install")
@click.option('-u', '--upstream', is_flag=True,
              help="use upstream archive")
@click.option('-a', '--archive', is_flag=True,
              help="use test deps from archive")
@click.option('-d', '--distro',
              help="override target distro  [default: current]")
@click.option('-F', '--file-list', 'input_file_lists', multiple=True,
              help=("specify text file listing one input file per line"
                    ", use '-' to read from stdin"))
@click.option('--ask/--no-ask', 'interactive',
              default=False, show_default=True,
              help="enable/disable interactive mode")
@click.help_option('-h', '--help',
                   help="show this help message")
def cli_test_dep(*args, **kwargs):
    """
    install or list testing dependencies
    """
    deps = test_dep(*args, **kwargs)
    if not kwargs.get('install', True):
        common.print_results(deps)


def test_dep(
        upstream=False,
        archive=False,
        input_files=None,
        input_file_lists=None,
        install=True,
        distro=None,
        interactive=False,
        project=None):
    """
    parse and optionally install testing dependencies

    pass install=False to only get list of deps without install

    returns list of test deps
    """
    action = 'installing' if install else 'listing'
    log.bold('%s testing deps', action)

    proj = project or Project()
    distro = adistro.distro_arg(distro, proj)
    log.info("target distro: %s", distro)

    infiles = common.parse_input_files(input_files, input_file_lists)
    archive, _ = parse_archive_args(
        proj, archive, upstream, infiles)

    tests = proj.get_tests_for_distro(distro)
    deps = tests.deps

    if install:
        n_deps = len(deps)
        if n_deps > 0:
            log.info("installing %s test deps...", n_deps)
            # TODO get pkgstyle for distro
            pkgstyle = get_pkgstyle_for_distro(distro)
            call_pkgstyle_fun(
                pkgstyle, 'install_build_deps',
                deps,
                distro=distro,
                interactive=interactive)
        else:
            log.info("no build deps to install")

    return deps


APKG_CLI_COMMANDS = [cli_test_dep]
