from pathlib import Path
import pytest
import shlex
import subprocess
import re

from apkg.cli import apkg
from apkg.project import Project
from apkg.util.run import cd
from apkg.util import test


APKG_BASE_DIR = Path(__file__).parents[2]
EXAMPLE_DIR = APKG_BASE_DIR / 'examples/multiple-sources'


@pytest.fixture(scope="module")
def repo_path(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("apkg_multiple_sources_")
    repo_path = test.init_testing_repo(EXAMPLE_DIR, str(tmpdir))
    return repo_path


@pytest.fixture(scope="module")
def proj(repo_path):
    return Project(repo_path.resolve())

RE_DEB_CH = r"Changes:\n apkg-ex-multiple-sources \(([^-]+)-([^)]+)\) unstable; .*"

def test_srcpkg_deb(proj, capsys):
    """
    test handling of components and compat level 5 features in deb packaging
    """
    with cd(proj.path.base):
        assert apkg('srcpkg', '-d', 'debian') == 0
        out, _ = capsys.readouterr()
        out_path = Path(out.strip()).resolve()
        assert out_path.exists()
        assert out_path.suffix == '.dsc'

        expected = {
            'apkg-ex-multiple-sources_0.1.orig{}.tar.gz'.format(suffix)
            for suffix in ('', '-extra', '-files')}
        assert set(p.name for p in out_path.parent.glob('*.orig*')) == expected

        changes_path = out_path.with_name(out_path.stem + '_source.changes')
        ch = changes_path.open('r').read()

    m = re.search(RE_DEB_CH, ch, re.DOTALL)
    assert m
    d_upstream, d_local = m.groups()
    assert d_upstream == '0.1'
    assert d_local == '1'

RE_RPM_CH = r"\* \w{3} \w{3} \d{2} \d{4} [^-]+- ([^-]+)-(\w+)"

def test_srcpkg_rpm(proj, capsys):
    """
    test handling of components and compat level 5 features in rpm packaging
    """
    with cd(proj.path.base):
        assert apkg('srcpkg', '-d', 'fedora') == 0
        out, _ = capsys.readouterr()
        out_path = Path(out.strip()).resolve()
        assert out_path.exists()
        assert out_path.name.endswith('.src.rpm')

        quoted = shlex.quote(str(out_path))
        expected = {
            'apkg-ex-multiple-sources-v0.1+repack.tar.gz',
            'apkg-ex-multiple-sources.spec',
            'extra-v0.5.tar.gz',
            'files.tar.gz',
        }
        listing = subprocess.getoutput("rpm2cpio %s | cpio -t --quiet" % quoted)
        files = set(listing.split('\n'))
        assert files == expected

        spec = subprocess.getoutput(("rpm2cpio %s | "
                                     "cpio -i --to-stdout '*.spec'") % quoted)

    chl = spec.split('%changelog\n')[-1]
    m = re.search(RE_RPM_CH, chl)
    assert m
    ver, rls = m.groups()
    assert ver == '0.1'
    assert rls == '1'
