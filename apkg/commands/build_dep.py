import click

from apkg import adistro
from apkg.cli import cli
from apkg.pkgstyle import call_pkgstyle_fun
from apkg.commands.get_archive import parse_archive_args
from apkg.commands.srcpkg import srcpkg as cmd_srcpkg
from apkg.commands.test_dep import test_dep as cmd_test_dep
from apkg.util import common
from apkg.log import getLogger
from apkg.project import Project


log = getLogger(__name__)


@cli.command(name="build-dep", aliases=['builddep'])
@click.argument('input_files', nargs=-1)
@click.option('-l', '--list', 'install', default=True, flag_value=False,
              help="list build deps only, don't install")
@click.option('-t', '--test-dep', is_flag=True,
              help="include testing deps as well")
@click.option('-u', '--upstream', is_flag=True,
              help="use upstream template / archive / srcpkg")
@click.option('-s', '--srcpkg', is_flag=True,
              help="use source package")
@click.option('-a', '--archive', is_flag=True,
              help="use template (/build srcpkg) from archive")
@click.option('-d', '--distro',
              help="override target distro  [default: current]")
@click.option('-F', '--file-list', 'input_file_lists', multiple=True,
              help=("specify text file listing one input file per line"
                    ", use '-' to read from stdin"))
@click.option('--ask/--no-ask', 'interactive',
              default=False, show_default=True,
              help="enable/disable interactive mode")
# TODO: once py3.5 is dropped, add hidden=True
@click.option('-y', '--yes', 'interactive', flag_value=False,
              help="compat alias for --no-ask")
@click.help_option('-h', '--help',
                   help="show this help message")
def cli_build_dep(*args, **kwargs):
    """
    install or list build dependencies
    """
    deps = build_dep(*args, **kwargs)
    if not kwargs.get('install', True):
        common.print_results(deps)


def build_dep(
        test_dep=False,
        upstream=False,
        srcpkg=False,
        archive=False,
        input_files=None,
        input_file_lists=None,
        install=True,
        distro=None,
        interactive=False,
        project=None):
    """
    parse and optionally install build dependencies

    pass install=False to only get list of deps without install

    returns list of build deps
    """
    action = 'installing' if install else 'listing'
    log.bold('%s build deps', action)

    proj = project or Project()
    distro = adistro.distro_arg(distro, proj)
    log.info("target distro: %s", distro)

    infiles = common.parse_input_files(input_files, input_file_lists)

    if srcpkg:
        # use source package to determine deps
        if archive or not infiles:
            # build source package
            srcpkg_files = cmd_srcpkg(
                archive=archive,
                distro=distro,
                input_files=input_files,
                input_file_lists=input_file_lists,
                upstream=upstream,
                project=proj)
        else:
            # use specified source package
            srcpkg_files = infiles

        common.ensure_input_files(srcpkg_files)
        srcpkg_path = srcpkg_files[0]

        # fetch pkgstyle (deb, rpm, arch, ...)
        template = proj.get_template_for_distro(distro)
        pkgstyle = template.pkgstyle

        log.info("build deps from srcpkg: %s", srcpkg_path)
        deps = call_pkgstyle_fun(
            pkgstyle, 'get_build_deps_from_srcpkg',
            srcpkg_path)

        if test_dep:
            log.warning("unable to load test deps from --srcpkg - skipping")
    else:
        # use tempalte to determine deps
        archive, archive_files = parse_archive_args(
            proj, archive, upstream, infiles)

        # fetch pkgstyle (deb, rpm, arch, ...)
        template = proj.get_template_for_distro(distro)
        pkgstyle = template.pkgstyle

        log.info("build deps from template: %s", template.path)
        deps = call_pkgstyle_fun(
            pkgstyle, 'get_build_deps_from_template',
            template.path, distro=distro)

        if test_dep:
            # include test deps as well
            tdeps = cmd_test_dep(
                install=False,
                upstream=upstream,
                archive=archive,
                input_files=archive_files)
            deps = sorted(set(deps).union(tdeps))

    if install:
        n_deps = len(deps)
        if n_deps > 0:
            log.info("installing %s build deps...", n_deps)
            call_pkgstyle_fun(
                pkgstyle, 'install_build_deps',
                deps,
                distro=distro,
                interactive=interactive)
        else:
            log.info("no build deps to install")

    return deps


APKG_CLI_COMMANDS = [cli_build_dep]
