import click

from apkg import ex
from apkg.log import getLogger
from apkg.project import Project
from apkg.util.git import git
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


@click.command(name='clean')
@click.option('-c', '--cache', is_flag=True,
              help="clean apkg cache metadata only")
@click.option('--hard', is_flag=True,
              help=("[!] HARD RESET project from VCS "
                    "and REMOVE extra files"))
@click.help_option('-h', '--help', help='show this help')
def cli_clean(*args, **kwargs):
    """
    clean apkg output directory (pkg/)
    """
    clean(*args, **kwargs)


def clean(cache=False, hard=False):
    proj = Project()
    if hard:
        if proj.vcs != 'git':
            raise ex.InvalidUsage(
                msg="HARD RESET currently requires git, "
                "but project VCS is: %s" % proj.vcs)
        git('reset', '--hard')
        git('clean', '-fxd')
        return

    if cache:
        log.bold("cleaning apkg cache")
        if proj.path.cache.exists():
            proj.path.cache.unlink()
            log.success("removed apkg cache: %s", proj.path.cache)
        else:
            log.success("apkg cache doesn't exist: %s", proj.path.cache)
        return

    log.bold("cleaning apkg output")
    if proj.path.output.exists():
        shutil.rmtree(proj.path.output)
        log.success("removed apkg output dir: %s", proj.path.output)
    else:
        log.success("apkg output dir doesn't exist: %s", proj.path.output)


APKG_CLI_COMMANDS = [cli_clean]
