"""
integration tests for apkg
"""
import os
import re
import subprocess

import pytest


@pytest.fixture(scope="module")
def build_dep():
    cmd = 'apkg build-dep'
    code, out = subprocess.getstatusoutput(cmd)
    assert code == 0, "build-dep ERROR (%s): %s" % (code, out)
    yield True


def test_apkg_ex_minimal_no_git():
    """
    test examples/minimal-no-git
    """
    old_cwd = os.getcwd()
    os.chdir('examples/minimal-no-git')
    try:
        cmd = ('apkg install --build-dep')
        code, out = subprocess.getstatusoutput(cmd)
        assert re.search(r'installed \d+ packages', out)
        assert code == 0, "ERROR (%s): %s" % (code, out)

        cmd = ('apkg test --test-dep')
        code, out = subprocess.getstatusoutput(cmd)
        assert code == 0, "ERROR (%s): %s" % (code, out)
    finally:
        os.chdir(old_cwd)


def test_apkg_full_pipe(build_dep):
    """
    test entire apkg pipeline using pipes

    This ensures:

    * apkg commands produce correct output
    * apkg commands are able to parse input from stdin (-F -)
    * apkg script is available from system shell

    Individual commands are tested in self tests.
    """
    cmd = ('apkg make-archive'
           ' | apkg srcpkg -a -F -'
           ' | apkg build -s -F -'
           ' | apkg install -C -F -')
    code, out = subprocess.getstatusoutput(cmd)
    assert code == 0, "ERROR (%s): %s" % (code, out)
    assert 'made archive:' in out
    assert 'made source package:' in out
    assert re.search(r'built \d+ packages', out)
    assert re.search(r'installed \d+ packages', out)
