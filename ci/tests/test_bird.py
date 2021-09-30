"""
integration tests for BIRD
"""
import glob
from pathlib import Path
import pytest

from apkg.util.run import cd
from apkg.util.git import git
from apkg.cli import apkg


BIRD_REPO_URL = 'https://gitlab.nic.cz/labs/bird.git'
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="module")
def clone_path(tmpdir_factory):
    """
    clone project repo once on module load and reuse it in individual tests
    """
    tmpd = tmpdir_factory.mktemp("apkg_test_bird_git")
    p = '%s/bird' % tmpd
    # XXX: using apkg-jru branch for now
    git('clone', '--recursive', '-b', 'apkg-jru',
        # fix SSL cert issues on old debian systems
        '-c', 'http.sslVerify=false',
        BIRD_REPO_URL, p)
    return Path(p)


@pytest.fixture(scope="module")
def repo_path(clone_path):
    """
    clone project repo and setup system for testing
    """
    with cd(clone_path):
        assert apkg('build-dep', '-y') == 0
    return clone_path


def test_bird_make_archive(repo_path, capsys):
    with cd(repo_path):
        assert apkg('make-archive') == 0
        ar_files = glob.glob('pkg/archives/dev/bird*')
    assert ar_files


def test_bird_get_archive(repo_path, capsys):
    with cd(repo_path):
        assert apkg('get-archive') == 0
        ar_files = glob.glob('pkg/archives/upstream/bird*')
    assert ar_files


def test_bird_srcpkg_dev(repo_path, capsys):
    with cd(repo_path):
        assert apkg('srcpkg') == 0
        out, _ = capsys.readouterr()
        for srcpkg in out.split("\n"):
            assert Path(srcpkg).exists()


def test_bird_build_dev(repo_path, capsys):
    with cd(repo_path):
        assert apkg('build') == 0
        out, _ = capsys.readouterr()
        for pkg in out.split("\n"):
            assert Path(pkg).exists()
