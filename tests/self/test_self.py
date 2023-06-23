from pathlib import Path
import os
import pytest
import re

from apkg.util import test
from apkg.util.run import cd
from apkg.util.git import git
from apkg.cli import apkg


APKG_BASE_DIR = Path(__file__).parents[2]


# NOTE(py35): use tmp_path instead of tmpdir
#             when py3.5 support is dropped

@pytest.fixture(scope="module")
def repo_path(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("apkg_test_repo_")
    repo_path = test.init_testing_repo(APKG_BASE_DIR, str(tmpdir))
    with cd(repo_path):
        # commit all changes for the purposes of testing, if any
        git('commit', '-a', '-m', 'TEST: uncommited changes from source',
            check=False)
    return repo_path


def test_import_command_modules():
    """
    test importing individual apkg command modules
    """
    import apkg.commands.build  # noqa
    import apkg.commands.build_dep  # noqa
    import apkg.commands.get_archive  # noqa
    import apkg.commands.install  # noqa
    import apkg.commands.make_archive  # noqa
    import apkg.commands.srcpkg  # noqa
    import apkg.commands.status  # noqa


def test_apkg_make_archive_cache(repo_path, caplog):
    with cd(repo_path):
        cache_path = Path('pkg/.cache.json')
        if cache_path.exists():
            os.remove(str(cache_path))

        # 1) run with --no-cache shouldn't create cache
        assert apkg('make-archive', '--no-cache') == 0
        assert not cache_path.exists()
        # 2) normal run should create cache
        assert apkg('make-archive') == 0
        assert cache_path.exists()
        # 3) should reuse archive from previous run
        assert apkg('make-archive') == 0
        # 4) --no-cache shouldn't reuse cached archive
        assert apkg('make-archive', '--no-cache') == 0

        # helpers to parse cumulative log output
        def is_relevant(r):
            if 'made archive' in r.message:
                return True
            if 'reuse cached archive' in r.message:
                return True
            return False

        def msg_head(r):
            head, _, _ = r.message.partition(' ')
            return head

        # pick relevant log lines's heads
        msgs = [msg_head(r) for r in caplog.records if is_relevant(r)]

        # make sure cached archive was reused only when it should
        assert msgs == [
            'made',  # 1) should create archive
            'made',  # 2) should create archive as 2) didn't cache it
            'reuse',  # 3) should reuse archive from 2)
            'made',  # 4) should create archive due to --no-cache
            ]


def test_apkg_get_archive_manual(repo_path, capsys):
    VERSION = '0.0.4'
    with cd(repo_path):
        assert apkg('get-archive', '--version', VERSION) == 0
    out, _ = capsys.readouterr()
    # first stdout line should be downloaded archive
    assert out.startswith("pkg/archives/upstream/apkg-v%s.tar.gz" % VERSION)


def test_apkg_get_archive_auto(repo_path, capsys):
    # this tests upstream version detection as well
    with cd(repo_path):
        assert apkg('get-archive') == 0
    out, _ = capsys.readouterr()
    # first stdout line should be downloaded archive
    assert out.startswith("pkg/archives/upstream/apkg-")


def test_apkg_srcpkg(repo_path, capsys):
    with cd(repo_path):
        assert apkg('srcpkg') == 0
    out, _ = capsys.readouterr()
    # first stdout line should be resulting source package
    assert re.match(r"pkg/srcpkgs/\S+/apkg\S+", out)


def test_apkg_build(repo_path, capsys):
    with cd(repo_path):
        assert apkg('build', '-b') == 0
    out, _ = capsys.readouterr()
    # at least one package should be printed
    assert re.match(r"pkg/pkgs/\S+/apkg\S+", out)


def assert_build_deps(deps_text):
    # make sure build deps contain at least one 'python*' dep
    for dep in deps_text.splitlines():
        if dep.startswith('python'):
            return
    assert False, "no python build dep detected"


def test_apkg_build_dep_tempalte(repo_path, capsys):
    # check listing build deps from tempalte works
    with cd(repo_path):
        assert apkg('build-dep', '-l') == 0
    out, _ = capsys.readouterr()
    assert_build_deps(out)


def test_apkg_build_dep_srcpkg(repo_path, capsys):
    # check listing build deps from srcpkg works
    # this includes srcpkg dev build
    with cd(repo_path):
        assert apkg('build-dep', '-s', '-l') == 0
    out, _ = capsys.readouterr()
    # check for a common build dep
    assert_build_deps(out)


def test_apkg_test(repo_path):
    with cd(repo_path):
        assert apkg('test', '--test-dep') == 0
