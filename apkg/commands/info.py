import click
import toml

import distro as distro_

from apkg.pkgstyle import PKGSTYLES
from apkg.log import getLogger, T
from apkg.project import Project


log = getLogger(__name__)


@click.group(name='info')
@click.help_option('-h', '--help', help='show command help')
def cli_info():
    """
    display various apkg information
    """


@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def config():
    """
    show apkg project configuration
    """
    proj = Project()
    msg = "project config: {t.bold}{fn}{t.normal}\n"
    msg = msg.format(fn=proj.path.config, t=T)
    log.info(msg)
    print(toml.dumps(proj.config))


@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def distro():
    """
    display current distro information
    """
    info = distro_.info()
    print(toml.dumps(info))


@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def distro_aliases():
    """
    list available distro aliases
    """
    proj = Project()
    if not proj.distro_aliases:
        log.info("no distro aliases defined")
        return

    for name, al in proj.distro_aliases.items():
        msg = "{t.bold}{name}{t.normal}: {rules}"
        print(msg.format(name=name, rules=al, t=T))


@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def pkgstyles():
    """
    list available packaging styles
    """
    for name, mod in PKGSTYLES.items():
        print("{t.bold}{name}{t.normal}".format(name=name, t=T))
        msg = "    module:   {t.magenta}{module}{t.normal}"
        print(msg.format(module=mod.__name__, t=T))
        msg = "    file:     {t.magenta}{fn}{t.normal}"
        print(msg.format(fn=mod.__file__, t=T))

        msg = "    distros:  "
        ds = ['{t.bold}%s{t.normal}' % d for d in mod.SUPPORTED_DISTROS]
        msg += ' | '.join(ds)
        print(msg.format(t=T))


@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def upstream_version():
    """
    show detected project upstream version
    """
    proj = Project()
    msg = "upstream version: {t.bold}{v}{t.normal}"
    print(msg.format(v=proj.upstream_version, t=T))


APKG_CLI_COMMANDS = [cli_info]