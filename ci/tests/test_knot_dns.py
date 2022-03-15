"""
integration tests for Knot DNS
"""
import glob
from pathlib import Path
import os
import pytest

from apkg.util.run import cd
from apkg.cli import apkg


KNOT_DNS_PATH = os.getenv('KNOT_DNS_PATH') or 'knot-dns'


@pytest.fixture(scope="module")
def archive_path():
    """
    find Knot DNS archive (created in previous CI step)
    """
    with cd(KNOT_DNS_PATH):
        paths = glob.glob('pkg/archives/dev/*')
    assert len(paths) == 1
    return paths[0]


def test_knot_srcpkg_ar(archive_path, capsys):
    with cd(KNOT_DNS_PATH):
        assert apkg('srcpkg', '--upstream', '--archive', archive_path) == 0
        out, _ = capsys.readouterr()
        for srcpkg in out.split("\n"):
            assert Path(srcpkg).exists()


def test_knot_build_ar(archive_path, capsys):
    with cd(KNOT_DNS_PATH):
        assert apkg('build', '-b', '-u', '-a', archive_path) == 0
        out, _ = capsys.readouterr()
        for pkg in out.split("\n"):
            assert Path(pkg).exists()
