"""apkg the cross-distro packaging automation tool

Usage: apkg <command> [<args>...]
       apkg <command> --help
       apkg [--debug | --verbose | --brief | --quiet] <command> [<args>...]
       apkg [--help | --version]

Commands:
  status                      show status of current project
  make-archive                create dev archive from current project
  get-archive                 download upstream source archive
  srcpkg                      create source package (to build packages from)
  build                       build packages
  build-dep                   install or list build dependencies
  install                     install local or distro packages

Options:
  -h --help     show help screen, can be used after a command
  --version     show version
""" # noqa
# TODO: Commands could be autogenerated but I don't want to slowdown
#       every invocation by parsing all commands.* modules.
#       A script for updating the __doc__ string here that is run
#       when dev adds a new command might be a decent compromise.

import importlib
import sys
from docopt import docopt

from apkg import __version__
from apkg import commands  # noqa: F401 (dynamic import)
from apkg import ex
from apkg.log import getLogger, T
import apkg.log as _log


log = getLogger(__name__)


def apkg(*cargs):
    """
    apkg CLI interface

    Execute apkg command with specified arguments
    and return shell friendly exit code.

        py> apkg('command', 'argument')

    is equivalent to

        $> apkg command argument

    This is a CLI wrapper around run_command() which returns actual command
    output instead of return code.
    """
    if len(cargs) == 0:
        # print full help when no commands/options are supplied
        cargs = cargs + ('--help',)
    else:
        # parse global arguments manually
        cargs, global_opts = parse_global_options(cargs)

    # parse arguments using docopt
    # (see __doc__ comment at the top of this file)
    args = docopt(__doc__,
                  argv=cargs,
                  version=__version__,
                  options_first=True)

    setup_logging(**global_opts)

    code = 1
    try:
        if args['<command>']:
            run_command(cargs)
            code = 0
    except ex.CommandFailed as e:
        # this was logged already
        code = e.exit_code
    except ex.ApkgException as e:
        print()
        print(T.bold_yellow(str(e)))
        code = e.exit_code

    return code


def run_command(cargs):
    """
    load apkg.commands.command and run its run_command() entry point
    with supplied arguments.
    """
    command = cargs[0]
    modname = 'apkg.commands.%s' % cmd2mod(command)
    spec = importlib.util.find_spec(modname)
    if not spec:
        raise ex.InvalidApkgCommand(command=command)
    # import command module
    mod = __import__(modname, fromlist=[''])
    return mod.run_command(cargs)


def run_alias(new_command, cargs):
    """
    helper function to run command using an alias

    changes cargs (with alias) to use new_command
    """
    alias, *rest = cargs
    new_cargs = [new_command] + rest
    log.verbose("alias: %s -> %s", alias, new_command)
    return run_command(new_cargs)


def cmd2mod(command):
    """translate command name to module name"""
    return command.replace('-', '_')


APKG_LOG_OPTIONS = {
    'debug': _log.DEBUG,
    'verbose': _log.VERBOSE,
    'brief': _log.WARN,
    'quiet': _log.ERROR,
}


def parse_global_options(cargs):
    """
    parse and remove global options from command arguments

    return (options_as_dict, new_command_args)
    """
    bool_opts = APKG_LOG_OPTIONS.keys()
    global_opts = {}
    args = list(cargs)

    for opt in bool_opts:
        arg = "--%s" % opt
        while arg in args:
            args.remove(arg)
            global_opts[opt] = True

    return tuple(args), global_opts


def setup_logging(**kwargs):
    log_level = 'default'
    for opt, log_level in APKG_LOG_OPTIONS.items():
        if kwargs.get(opt):
            _log.set_log_level(log_level)
            log.verbose("log level: --%s (%s)", opt, log_level)
            break


def main():
    """
    apkg console_scripts entry point
    """
    cargs = sys.argv[1:]
    sys.exit(apkg(*cargs))


if __name__ == '__main__':
    main()
