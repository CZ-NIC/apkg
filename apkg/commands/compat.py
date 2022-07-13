import click
from packaging import version

from apkg import __version__
from apkg import compat as compat_
from apkg import ex
from apkg.log import getLogger, T
from apkg.project import Project
from apkg.util.upstreamversion import latest_apkg_version


log = getLogger(__name__)


@click.command(name='compat')
@click.help_option('-h', '--help', help='show this help')
@click.option('--latest/--no-latest', default=True, show_default=True,
              help="check latest apkg version/compat level online")
@click.option('-n', '--notes', default=0,
              help="only show compat level upgrade notes since level")
def cli_compat(*args, **kwargs):
    """
    check apkg compat level

    display hints on howto set it properly if it isn't current

    return exit code 1 if compat check failed
    """
    ok = compat(*args, **kwargs)
    if not ok:
        raise ex.QuietExit()


def compat(latest=True, notes=None):
    current_compat = compat_.COMPAT_LEVEL

    if notes:
        notes_ = compat_.get_level_notes(notes, current_compat)
        print_notes(notes_)
        return True

    proj = Project(auto_compat=False)
    proj_compat = proj.compat_level
    current_version = version.parse(__version__)

    if latest:
        latest_version = version.parse(latest_apkg_version())
        latest_compat = compat_.get_upstream_compat_level(latest_version) or 1

    msg = "project compat level:       {t.bold}{level}{t.normal}"
    print(msg.format(level=proj_compat or 'N/A', t=T))

    msg = "current apkg compat level:  {t.bold}{level}{t.normal}"
    print(msg.format(level=current_compat, t=T))

    if latest:
        msg = "latest apkg compat level:   {t.bold}{level}{t.normal}"
        print(msg.format(level=latest_compat, t=T))

    print()

    msg = "current apkg version:  {t.bold}{v}{t.normal}"
    print(msg.format(v=current_version, t=T))

    if latest:
        msg = "latest apkg version:   {t.bold}{v}{t.normal}"
        print(msg.format(v=latest_version, t=T))

    print()

    if latest and current_compat < latest_compat:
        print("latest apkg-{v} has newer compat level"
              " {l} - consider upgrading apkg\n".format(
                  l=latest_compat, v=latest_version))

    if not proj_compat:
        print("{t.bold_yellow}⚠ apkg.compat level isn't set in config"
              "{t.normal}".format(t=T))
        print("\nPlease consider adding\n\n"
              "    {t.command}[apkg]\n"
              "    compat = {ccl}{t.normal}\n\n"
              "to project config: {t.bold}{cfg}{t.normal}\n".format(
                  ccl=current_compat, cfg=proj.path.config, t=T))
        print("This will ensure compatibility between apkg versions.")
        return False

    if proj_compat < current_compat:
        print("{t.bold_yellow}⚠ project compat level {pcl} is older than"
              " current {ccl}{t.normal}".format(
                  pcl=proj_compat, ccl=current_compat, t=T))
        print("\nPlease consider bumping\n\n"
              "    {t.command}[apkg]\n"
              "    compat = {ccl}{t.normal}\n\n"
              "in project config: {t.bold}{cfg}{t.normal}".format(
                  ccl=current_compat, cfg=proj.path.config, t=T))
        print("\nInspect following upgrade notes:")
        print_notes(compat_.get_level_notes(proj_compat, current_compat))
        return False

    if proj_compat > current_compat:
        print("{t.bold_red}❌ project compat level {pl} is newer than"
              " current {cl} - please upgrade apkg!{t.normal}".format(
                  pl=proj_compat, cl=current_compat, t=T))
        return False

    print("{t.bold_green}✔ project compat level {l} matches installed"
          " apkg version{t.normal}".format(l=current_compat, t=T))
    return True


def print_notes(notes):
    for level, (ver, note) in notes.items():
        print("\n{t.magenta}# COMPAT LEVEL {l}\n\n"
              "{t.normal}Introduced in apkg-{v}\n".format(v=ver, l=level, t=T))
        print(note)


APKG_CLI_COMMANDS = [cli_compat]
