"""
apkg the cross-distro packaging automation tool
"""
import os
import pkgutil
import sys

import click

from apkg import __version__
from apkg import commands
from apkg import ex
from apkg.log import getLogger, T
from apkg.util.run import log_cmd_fail
import apkg.log as _log


log = getLogger(__name__)


CLI_LOG_LEVELS = {
    'debug': _log.DEBUG,
    'verbose': _log.VERBOSE,
    'info': _log.INFO,
    'brief': _log.WARN,
    'quiet': _log.ERROR,
}


class ClickApkgGroup(click.Group):
    """
    custom click group for handling command aliases

    based on https://github.com/click-contrib/click-aliases
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._commands = {}
        self._aliases = {}

    def command(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super().command(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def group(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super().group(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def resolve_alias(self, cmd_name):
        if cmd_name in self._aliases:
            return self._aliases[cmd_name]
        return cmd_name

    def get_command(self, ctx, cmd_name):
        cmd_name = self.resolve_alias(cmd_name)
        command = super().get_command(ctx, cmd_name)
        return command


@click.group(cls=ClickApkgGroup)
@click.option('-L', '--log-level',
              default='info', show_default=True,
              type=click.Choice(CLI_LOG_LEVELS.keys()),
              help="set log level")
@click.help_option('-h', '--help',
                   help="show this help message")
@click.version_option(__version__, message='%(version)s',
                      help="show apkg version")
def cli(log_level='info'):
    """
    apkg the upstream packaging automation tool
    """
    level = CLI_LOG_LEVELS[log_level]
    _log.set_log_level(level)
    log.verbose("apkg version: %s", __version__)
    log.verbose("log level: %s (%s)", log_level.upper(), _log.get_log_level())


def apkg(*args):
    """
    apkg shell interface

    Execute apkg command with specified arguments
    and return shell friendly exit code.

        py> apkg('command', 'argument')

    is equivalent to

        $> apkg command argument

    This is a shell-friendly wrapper around cli()
    which always returns numeric exit code
    as opposed to raising exceptions.

    If you're using apkg from python you probably want to use
    cli() or apkg.commands.* modules directly instead.
    """

    code = 1
    try:
        # pylint: disable=unexpected-keyword-arg
        cli(args, standalone_mode=False)
        code = 0
    except ex.CommandFailed as e:
        log_cmd_fail(e.kwargs['cmdout'])
        code = e.returncode
    except ex.PkgTestFail as e:
        # already logged
        code = e.returncode
    except ex.QuietExit as e:
        code = e.returncode
    except ex.ApkgException as e:
        print(T.bold_yellow(str(e)))
        code = e.returncode
    except click.exceptions.ClickException as e:
        print(T.yellow(str(e)))
        code = ex.InvalidUsage.returncode

    return code


def main():
    """
    apkg console_scripts entry point
    """
    cargs = sys.argv[1:]
    sys.exit(apkg(*cargs))


def __load_commands():
    """
    load available apkg commands

    should only be called once on module load
    """
    pkgpath = os.path.dirname(commands.__file__)
    for _, modname, _ in pkgutil.iter_modules([pkgpath]):
        modpath = "apkg.commands.%s" % (modname)
        mod = __import__(modpath, fromlist=[''])
        cmds = getattr(mod, 'APKG_CLI_COMMANDS', None)
        if not cmds:
            log.warning('command module with no CLI commands: %s', modpath)
            continue
        for cmd in cmds:
            cli.add_command(cmd)


__load_commands()


if __name__ == '__main__':
    main()
