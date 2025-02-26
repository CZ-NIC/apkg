import json

import click
import distro as distro_mod
import importlib
from pathlib import Path
import sys

from apkg import adistro
from apkg.pkgstyle import PKGSTYLES
from apkg import pkgtemplate
from apkg.log import getLogger, T
from apkg.project import Project
from apkg import terminal
from apkg.util import common
from apkg.util import toml


log = getLogger(__name__)


RUNTIME_DEPS = [
    'bs4',
    'click',
    'distro',
    'jinja2',
    'packaging',
    'requests',
]

BUILD_DEPS = [
    'build',
    'setuptools',
]


@click.group(name='info')
@click.help_option('-h', '--help', help='show command help')
def cli_info():
    """
    show various apkg information
    """


@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def apkg_deps():
    """
    show apkg dependencies info
    """
    print("{t.bold}Python interpreter{t.normal}:".format(t=T))
    py_cmd = Path(sys.executable).stem
    s = ("{t.green}{c}{t.normal} {t.cyan}{v}{t.normal}: "
         "{t.bold}{p}{t.normal}")
    if sys.prefix != sys.base_prefix:
        s += ' - {t.magenta}venv{t.normal}'
    print(s.format(c=py_cmd, v=sys.version, p=sys.executable, t=T))

    print("\n{t.bold}core dependencies{t.normal}:".format(t=T))
    for dep in RUNTIME_DEPS:
        print(modinfo_t(dep))

    print("\n{t.bold}dynamic dependencies{t.normal}:".format(t=T))
    print(modinfo_t(toml.LOAD_LIB, 'TOML load'))
    print(modinfo_t(toml.DUMP_LIB, 'TOML dump', failc='yellow'))
    print(modinfo_t(terminal.COLOR_LIB, 'terminal colors', failc='yellow'))

    print("\n{t.bold}build dependencies{t.normal}:".format(t=T))
    for dep in BUILD_DEPS:
        print(modinfo_t(dep))


@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def cache():
    """
    show apkg cache contents
    """
    proj = Project()
    cache_str = "{t.bold}{fn}{t.normal}".format(fn=proj.path.cache, t=T)
    if proj.path.cache.exists():
        log.info("apkg cache: %s", cache_str)
        cdata = json.load(proj.path.cache.open('rt'))
        print(json.dumps(cdata, indent=4))
    else:
        log.info("apkg cache doesn't exist: %s", cache_str)


@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def config():
    """
    show apkg project configuration
    """
    proj = Project()
    config_str = "{t.bold}{fn}{t.normal}".format(fn=proj.path.config, t=T)
    if proj.path.config.exists():
        log.info("project config: %s\n", config_str)
    else:
        log.info("project config doesn't exist: %s", config_str)

    if proj.config:
        print(toml.dumps(proj.config))


# pylint: disable=redefined-outer-name
@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def distro():
    """
    show current distro information
    """
    info = distro_mod.info()
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
@click.option('-d', '--distro',
              help="set target distro  [default: current]")
@click.option('-c', '--custom', is_flag=True,
              help="only show custom variables per source")
@click.help_option('-h', '--help', help='show command help')
def template_variables(distro=None, custom=False):
    """
    show variables available in packaging template
    """
    proj = Project()
    distro = adistro.distro_arg(distro, proj)
    log.info("target distro: %s", distro)
    template = proj.get_template_for_distro(distro)
    if not custom:
        tvars = {'distro': distro}
        tvars = template.template_vars(tvars)
        print(toml.dumps(common.serialize(tvars)))
        return

    # custom variables
    tvars = pkgtemplate.DUMMY_VARS
    tvars['distro'] = distro
    for vsrc in proj.variables_sources:
        print("# variables from %s: %s" % (vsrc.src_attr, vsrc.src_val))
        custom_tvars = vsrc.get_variables(tvars)
        print(toml.dumps(common.serialize(custom_tvars)))
        tvars.update(custom_tvars)


@cli_info.command()
@click.help_option('-h', '--help', help='show command help')
def upstream_version():
    """
    show detected project upstream version
    """
    proj = Project()
    msg = "upstream version: {t.bold}{v}{t.normal}"
    print(msg.format(v=proj.upstream_version, t=T))


def modinfo_t(modname, desc=None, failc='red'):
    if not modname:
        s = "{d}: {t.%s}no supported module found{t.normal}" % (failc)
        s = s.format(d=desc, t=T)
        return s

    mod = None
    err = None
    try:
        mod = importlib.import_module(modname)
    except Exception as e:
        err = e

    if mod:
        s = ''
        if desc:
            s += '%s: ' % desc
        s += "{t.green}{m}{t.normal}"
        if hasattr(mod, '__version__'):
            ver = getattr(mod, '__version__')
            s += " {t.cyan}%s{t.normal}" % ver
        s += ": {t.bold}{p}{t.normal}"
        return s.format(m=modname, p=Path(mod.__file__).parent, t=T)

    s = ''
    if desc:
        s += '%s: ' % desc
    s += ("{t.red}{m}{t.normal}: {t.bold_red}{et}{t.normal}: "
          "{t.normal}{e}{t.normal}")
    return s.format(m=modname, et=err.__class__.__name__, e=err, t=T)


APKG_CLI_COMMANDS = [cli_info]
