"""
integration tests for Knot Resolver
"""
import glob
from pathlib import Path
import os
import pytest

from apkg.util.run import cd
from apkg.util.git import git
from apkg.cli import apkg


KRESD_REPO_URL = 'https://gitlab.nic.cz/knot/knot-resolver.git'
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="module")
def clone_path(tmpdir_factory):
    """
    clone project repo once on module load and reuse it in individual tests
    """
    tmpd = tmpdir_factory.mktemp("apkg_test_kresd_git")
    p = '%s/knot-resolver' % tmpd
    branch = os.getenv('KNOT_RESOLVER_BRANCH') or 'master'
    git('clone', '--recursive', '-b', branch, KRESD_REPO_URL, p)
    return Path(p)


@pytest.fixture(scope="module")
def repo_path(clone_path):
    """
    clone project repo and setup system for testing
    """
    with cd(clone_path):
        assert apkg('build-dep', '-y') == 0
    return clone_path


def test_kresd_make_archive(repo_path, capsys):
    with cd(repo_path):
        assert apkg('make-archive') == 0
        ar_files = glob.glob('pkg/archives/dev/knot-resolver*')
    assert ar_files


def test_kresd_get_archive(repo_path, capsys):
    with cd(repo_path):
        assert apkg('get-archive') == 0
        ar_files = glob.glob('pkg/archives/upstream/knot-resolver*')
    assert ar_files


def test_kresd_srcpkg_dev(repo_path, capsys):
    with cd(repo_path):
        assert apkg('srcpkg') == 0
        out, _ = capsys.readouterr()
        for srcpkg in out.split("\n"):
            assert Path(srcpkg).exists()


def test_kresd_build_dev(repo_path, capsys):
    with cd(repo_path):
        assert apkg('build', '-b') == 0
        out, _ = capsys.readouterr()
        for pkg in out.split("\n"):
            assert Path(pkg).exists()
