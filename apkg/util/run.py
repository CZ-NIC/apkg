# -*- encoding: utf-8 -*-
from contextlib import contextmanager
import os
import subprocess
import sys
import shlex

from apkg import ex
from apkg.log import getLogger, T, INFO, get_log_level


log = getLogger(__name__)


IS_ROOT = False
if os.geteuid() == 0:
    IS_ROOT = True


def log_cmd_fail(cmd, cout):
    log.error("command failed: %s", T.command(cmd))
    if cout:
        log.bold("stdout:")
        log.info(cout)
    if cout.stderr:
        log.bold("stderr:")
        log.info(cout.stderr)


def run(*cmd, **kwargs):
    """
    run system commands easily - a subprocess.Popen wrapper

    run('echo', 'hello world')
    """
    fatal = kwargs.get('fatal', True)
    direct = kwargs.get('direct', False)
    silent = kwargs.get('silent', False)
    log_cmd = kwargs.get('log_cmd', True)
    log_fail = kwargs.get('log_fail', True)
    log_fun = kwargs.get('log_fun', log.command)
    _input = kwargs.get('input')
    print_stdout = kwargs.get('print_stdout', False)
    print_stderr = kwargs.get('print_stderr', False)
    print_output = kwargs.get('print_output', False)
    env = kwargs.get('env', None)

    cmd = [str(c) for c in cmd]
    cmd_str = ' '.join([shlex.quote(c) for c in cmd])

    if silent:
        log_cmd = False
        log_fail = False
        print_stdout = False
        print_stderr = False

    if print_output:
        print_stdout = True
        print_stderr = True

    if _input:
        stdin = subprocess.PIPE
        if not isinstance(_input, bytes):
            _input = bytes(_input, 'utf-8')
    else:
        stdin = None

    if direct == 'auto':
        direct = bool(sys.stdout.isatty() and get_log_level() <= INFO)
    if direct:
        stdout = None
        stderr = None
    else:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE

    if log_cmd:
        log_fun(cmd_str)

    try:
        prc = subprocess.Popen(cmd, stdin=stdin, stdout=stdout,
                               stderr=stderr, env=env)
    except OSError:
        raise ex.CommandNotFound(cmd=cmd[0])
    out, err = prc.communicate(input=_input)

    if isinstance(out, bytes):
        out = out.decode('utf-8')
    if isinstance(err, bytes):
        err = err.decode('utf-8')

    if out:
        out = out.rstrip()
        if print_stdout:
            log.info(out)
    else:
        out = ''

    if err:
        err = err.rstrip()
        if print_stderr:
            log.info(err)
    else:
        err = ''

    cout = CommandOutput(out)
    cout.stderr = err
    cout.return_code = prc.returncode
    cout.cmd = cmd
    cout.cmd_str = cmd_str
    if prc.returncode != 0:
        if log_fail:
            log_cmd_fail(cmd_str, cout)
        if fatal:
            raise ex.CommandFailed(cmd=cmd_str, out=cout)
    return cout


def sudo(*cmd, **kwargs):
    preserve_env = kwargs.pop('preserve_env', False)
    if 'env' in kwargs:
        preserve_env = True
    if not IS_ROOT:
        sudo_cmd = ['sudo']
        if preserve_env:
            sudo_cmd.append('-E')
        cmd = sudo_cmd + list(cmd)
        kwargs['log_fun'] = log.sudo
    return run(*cmd, **kwargs)


@contextmanager
def cd(newdir):
    """
    Temporarily change current directory.
    """
    olddir = os.getcwd()
    oldpwd = os.environ.get('PWD')
    newpath = os.path.abspath(os.path.expanduser(str(newdir)))
    os.chdir(newpath)
    os.environ['PWD'] = newpath
    try:
        yield
    finally:
        os.chdir(olddir)
        if oldpwd is not None:
            os.environ['PWD'] = oldpwd
        else:
            del os.environ['PWD']


class ShellCommand:
    command = None

    def __init__(self):
        if self.command is None:
            self.command = self.__class__.__name__.lower()

    def __call__(self, *params, **kwargs):
        return run(self.command, *params, **kwargs)


class CommandOutput(str):
    """
    Just a string subclass with attribute access.
    """
    cmd = None
    cmd_str = None
    stderr = None
    return_code = None

    @property
    def success(self):
        return self.return_code == 0
