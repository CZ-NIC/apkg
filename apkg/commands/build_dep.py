import click

from apkg import adistro
from apkg.cli import cli
from apkg.pkgstyle import call_pkgstyle_fun
from apkg.commands.get_archive import get_archive
from apkg.commands.srcpkg import srcpkg as make_srcpkg
from apkg.util import common
from apkg.log import getLogger
from apkg.project import Project
from apkg.util.archive import unpack_archive


log = getLogger(__name__)


@cli.command(name="build-dep", aliases=['builddep'])
@click.argument('input_files', nargs=-1)
@click.option('-l', '--list', 'install', default=True, flag_value=False,
              help="list build deps only, don't install")
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

    # fetch pkgstyle (deb, rpm, arch, ...)
    template = proj.get_template_for_distro(distro)
    pkgstyle = template.pkgstyle

    infiles = common.parse_input_files(input_files, input_file_lists)

    if srcpkg:
        # use source package to determine deps
        if archive or not infiles:
            # build source package
            srcpkg_files = make_srcpkg(
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

        log.info("build deps from srcpkg: %s", srcpkg_path)
        deps = call_pkgstyle_fun(
            pkgstyle, 'get_build_deps_from_srcpkg',
            srcpkg_path)
    else:
        # use tempalte to determine deps
        if archive:
            archive_files = infiles

        if upstream:
            archive = True
            archive_files = get_archive(project=proj)

        if archive:
            common.ensure_input_files(archive_files)
            archive_path = archive_files[0]
            log.info("unpacking archive: %s", archive_path)
            unpack_path = unpack_archive(
                archive_path, proj.unpacked_archive_path)
            log.info("loading template from archive: %s", unpack_path)
            # load project with input_path from archive
            aproj = Project(path=unpack_path)
            template = aproj.get_template_for_distro(distro)

        log.info("build deps from template: %s", template.path)
        deps = call_pkgstyle_fun(
            pkgstyle, 'get_build_deps_from_template',
            template.path, distro=distro)

    if install:
        log.info("installing %s build deps...", len(deps))
        call_pkgstyle_fun(
            pkgstyle, 'install_build_deps',
            deps,
            distro=distro,
            interactive=interactive)

    return deps


APKG_CLI_COMMANDS = [cli_build_dep]
