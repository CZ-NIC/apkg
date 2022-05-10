import pytest

from apkg.util.run import run


@pytest.mark.parametrize("args_list", [False, True])
@pytest.mark.parametrize("tee", [False, True])
def test_run_exec(args_list, tee):
    cmd = ['echo', '-e', 'a', 'b']
    if args_list:
        o = run(cmd, tee=tee)
    else:
        o = run(*cmd, tee=tee)
    assert o == 'a b'
    assert o.args == cmd
    assert o.args_str == 'echo -e a b'
    assert o.returncode == 0


@pytest.mark.parametrize("args_list", [False, True])
@pytest.mark.parametrize("tee", [False, True])
def test_run_shell(args_list, tee):
    cmd = 'echo "some\nTEST\nstring" | grep TEST'
    if args_list:
        o = run([cmd], shell=True, tee=tee)
    else:
        o = run(cmd, shell=True, tee=tee)
    assert o == 'TEST'
    assert o.args == [cmd]
    assert o.args_str == cmd
    assert o.returncode == 0
