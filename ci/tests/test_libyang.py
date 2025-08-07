"""
integration tests for libyang
"""
import glob
from pathlib import Path
import os
import pytest

from apkg.util.run import cd
from apkg.util.git import git
from apkg.cli import apkg


LIBYANG_REPO_URL = 'https://github.com/CESNET/libyang'
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="module")
def clone_path(tmp_path_factory):
    """
    clone project repo once on module load and reuse it in individual tests
    """
    tmpd = tmp_path_factory.mktemp("apkg_test_libyang_git")
    p = '%s/libyang' % tmpd
    branch = os.getenv('LIBYANG_BRANCH') or 'master'
    git('clone', '--recursive', '-b', branch, LIBYANG_REPO_URL, p)
    return Path(p)


@pytest.fixture(scope="module")
def repo_path(clone_path):
    """
    clone project repo and setup system for testing
    """
    with cd(clone_path):
        assert apkg('build-dep', '-y') == 0
    return clone_path


def test_libyang_make_archive(repo_path, capsys):
    with cd(repo_path):
        assert apkg('make-archive') == 0
        ar_files = glob.glob('pkg/archives/dev/libyang*')
    assert ar_files


def test_libyang_get_archive(repo_path, capsys):
    with cd(repo_path):
        assert apkg('get-archive') == 0
        ar_files = glob.glob('pkg/archives/upstream/libyang*')
    assert ar_files


def test_libyang_srcpkg_dev(repo_path, capsys):
    with cd(repo_path):
        assert apkg('srcpkg') == 0
        out, _ = capsys.readouterr()
        for srcpkg in out.split("\n"):
            assert Path(srcpkg).exists()


def test_libyang_build_dev(repo_path, capsys):
    with cd(repo_path):
        assert apkg('build') == 0
        out, _ = capsys.readouterr()
        for pkg in out.split("\n"):
            assert Path(pkg).exists()


def test_libyang_install_dev(repo_path):
    with cd(repo_path):
        assert apkg('install') == 0
