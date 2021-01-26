# -*- encoding: utf-8 -*-
from contextlib import contextmanager
import os
import subprocess

from apkg.compat import py35path
from apkg import exception
from apkg.log import getLogger, T


log = getLogger(__name__)


IS_ROOT = False
if os.geteuid() == 0:
    IS_ROOT = True


def log_cmd_fail(cmd, cout):
    log.error("command failed: %s" % T.command(cmd))
    if cout:
        log.bold("stdout:")
        log.info(cout)
    if cout.stderr:
        log.bold("stderr:")
        log.info(cout.stderr)


def run(*cmd, **kwargs):
    fatal = kwargs.get('fatal', True)
    direct = kwargs.get('direct', False)
    log_cmd = kwargs.get('log_cmd', True)
    log_fail = kwargs.get('log_fail', True)
    log_fun = kwargs.get('log_fun', log.command)
    input = kwargs.get('input')
    print_stdout = kwargs.get('print_stdout', False)
    print_stderr = kwargs.get('print_stderr', False)
    print_output = kwargs.get('print_output', False)
    env = kwargs.get('env', None)

    # TODO: escape parameters with whitespace
    cmd = [str(c) for c in cmd]
    cmd_str = ' '.join(cmd)

    if log_cmd:
        log_fun(cmd_str)

    if print_output:
        print_stdout = True
        print_stderr = True

    if input:
        stdin = subprocess.PIPE
    else:
        stdin = None

    if direct:
        stdout = None
        stderr = None
    else:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE

    try:
        prc = subprocess.Popen(cmd, stdin=stdin, stdout=stdout,
                               stderr=stderr, env=env)
    except OSError:
        raise exception.CommandNotFound(cmd=cmd[0])
    out, err = prc.communicate(input=input)

    if type(out) == bytes:
        out = out.decode('utf-8')
    if type(err) == bytes:
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
    cout.cmd = cmd_str
    if prc.returncode != 0:
        if log_fail:
            log_cmd_fail(cmd_str, cout)
        if fatal:
            raise exception.CommandFailed(cmd=cmd, out=cout)
    return cout


def sudo(*cmd, **kwargs):
    preserve_env = kwargs.pop('preserve_env', False)
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
    os.chdir(os.path.expanduser(py35path(newdir)))
    try:
        yield
    finally:
        os.chdir(olddir)


class ShellCommand(object):
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
    @property
    def success(self):
        return self.return_code == 0
