"""
run system commands easily

see primary run() function
"""
import asyncio
from contextlib import contextmanager
import os
from pathlib import Path
import subprocess
import sys
import shlex
try:
    from shlex import join
except ImportError:
    from subprocess import list2cmdline as join

from packaging import version

from apkg import ex
from apkg.log import getLogger, T, COMMAND, get_log_level


log = getLogger(__name__)


IS_ROOT = os.geteuid() == 0
PY_VERSION = version.parse('%s.%s' % (sys.version_info[:2]))
# Require python 3.6 for tee feature.
CAN_TEE = PY_VERSION >= version.parse('3.6')


def run(cmd,
        *args,
        check=True,
        tee='auto',
        quiet=False,
        log_fun=log.command,
        **kwargs):
    """
    subprocess.run wrapper with tee and logging powers

    You can use this in following ways:

        run('command', 'arg1', 'arg2')
        run(['command', 'arg1', 'arg2'])
        run('command arg1 arg2', shell=True)

    Differences from subprocess.run:

    * can both capture and output stdout/stderr when tee is set (asyncio)
    * return str subclass with CompletedProcess args - easy to process
    * log commands by default for easy debugging
    * check=True by default - failing commands will raise ex.CommandFailed
    * ex.CommandFailed and ex.CommandNotFound can be raised

    Params:
        cmd: command to run - a str or a List[str]
        *args: optional List[str] of command arguments
        check: raise ex.CommandFailed on command failure
        tee: both capture and output stdout/stderr (using asyncio)
        quiet: disable tee and command logging
        log_fun: function to log command with (None to disable)

    Return:
        CommandOutput is a str subclass with subprocess.ProcessCompleted
        args allowing for direct string processing with optional access to
        process information:

        out = run('echo', 'hello world')

        assert out == 'hello world'
        print(f'command: {out.args_str})
        print(f'return code: {out.returncode}')
        print(f'stdout:\n{out}')
        print(f'stderr:\n{out.stderr}')
    """
    cmd = parse_cmd_args(cmd, *args)
    shell = kwargs.get('shell', False)
    if shell:
        cmd_str = cmd[0]
    else:
        cmd_str = join(cmd)

    if quiet:
        log_fun = log.verbose_command
        tee = False
    elif tee == 'auto':
        tee = bool(get_log_level() <= COMMAND)

    if tee and not CAN_TEE:
        log.warning("can't tee on python < 3.6"
                    " - command output won't be printed")
        tee = False

    if log_fun:
        log_fun(cmd_str)

    if tee:
        try:
            loop = asyncio.get_event_loop_policy().get_event_loop()
            result = loop.run_until_complete(_tee(*cmd, **kwargs))
        except FileNotFoundError:
            raise ex.CommandNotFound(cmd=cmd_str)
    else:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                universal_newlines=True,
                **kwargs)
        except OSError:
            raise ex.CommandNotFound(cmd=cmd_str)

    cmdout = CommandOutput(result, shell=shell)

    if check and result.returncode != 0:
        raise ex.CommandFailed(cmdout=cmdout)

    return cmdout


async def _tee(*args, shell=False, **kwargs):
    """
    async version of subprocess.run() which can both
    stream and capture stdout/stderr like unix tee

    Print both stdout/stderr to stderr in order not to polute
    stdout with random command output.

    Use run() function from this module with tee=True
    to use this in a convenient way.
    """
    if shell:
        process = await asyncio.create_subprocess_shell(
            args[0],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **kwargs
        )
    else:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **kwargs
        )
    out = []
    err = []

    def tee_fun(line, sink):
        line_str = line.decode("utf-8").rstrip()
        sink.append(line_str)
        print(line_str, file=sys.stderr)

    loop = asyncio.get_event_loop_policy().get_event_loop()
    tasks = []
    if process.stdout:
        tasks.append(loop.create_task(_read_stream(
            process.stdout, lambda x: tee_fun(x, out))))
    if process.stderr:
        tasks.append(loop.create_task(_read_stream(
            process.stderr, lambda x: tee_fun(x, err))))

    await asyncio.wait(set(tasks))

    stdout = os.linesep.join(out) + os.linesep
    stderr = os.linesep.join(err) + os.linesep

    return subprocess.CompletedProcess(
        args=list(args),
        returncode=await process.wait(),
        stdout=stdout,
        stderr=stderr,
    )


async def _read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line:
            callback(line)
        else:
            break


def sudo(*cmd, **kwargs):
    """
    run command with sudo
    """
    preserve_env = kwargs.pop('preserve_env', False)
    if 'env' in kwargs:
        preserve_env = True
    if not IS_ROOT:
        shell = kwargs.get('shell', False)
        sudo_cmd = ['sudo']
        if preserve_env:
            sudo_cmd.append('-E')
        if shell:
            shcmd = shlex.quote(cmd[0])
            cmd = ["%s bash -c %s" % (join(sudo_cmd), shcmd)]
        else:
            cmd = parse_cmd_args(*cmd)
            cmd = sudo_cmd + cmd
        if 'log_fun' not in kwargs:
            kwargs['log_fun'] = log.sudo
    return run(*cmd, **kwargs)


def parse_cmd_args(cmd, *args):
    if isinstance(cmd, (str, Path)):
        cmd = [cmd]
    if args:
        cmd.extend(args)
    # convert Path and others to str
    cmd = [str(c) for c in cmd]
    return cmd


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


class CommandOutput(str):
    """
    A str subclass with CompletedProcess args

    Useful for returning command stdout for easy processing
    while preserving command run information

    Additionally, args_str is available with command args
    properly joined into a string.
    """
    # pylint: disable=unused-argument
    def __new__(cls, result, shell):
        out = result.stdout.rstrip()
        return str.__new__(cls, out)

    def __init__(self, result, shell=False):
        self.args = result.args
        self.shell = shell
        if shell:
            self.args_str = self.args[0]
        else:
            self.args_str = join(self.args)
        self.returncode = result.returncode
        self.stdout = self
        self.stderr = result.stderr.rstrip()
        str.__init__(self)

    @property
    def success(self):
        return self.returncode == 0


class ShellCommand:
    command = None

    def __init__(self):
        if self.command is None:
            self.command = self.__class__.__name__.lower()

    def __call__(self, *params, **kwargs):
        return run(self.command, *params, **kwargs)


def log_cmd_fail(cmdout):
    log.error("command failed: %s", T.command(cmdout.args_str))
    if cmdout.stdout:
        log.bold("stdout:")
        log.info(cmdout.stdout)
    if cmdout.stderr:
        log.bold("stderr:")
        log.info(cmdout.stderr)
