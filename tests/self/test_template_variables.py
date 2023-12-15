from pathlib import Path
import pytest
import re

from apkg.cli import apkg
from apkg.project import Project
from apkg.util.run import cd
from apkg.util import test


APKG_BASE_DIR = Path(__file__).parents[2]
EXAMPLE_DIR = APKG_BASE_DIR / 'examples/template-variables'


@pytest.fixture(scope="module")
def repo_path(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("apkg_test_templates_")
    repo_path = test.init_testing_repo(EXAMPLE_DIR, str(tmpdir))
    return repo_path


@pytest.fixture(scope="module")
def proj(repo_path):
    return Project(repo_path.resolve())


RE_DEB_CH = r"""apkg-ex-template-variables \(0.1-1~(\w+)\) (\w+); urgency=medium

  \* upstream version 0.1 for (?:\w+)(?: [\w.]+)? (.*)
  \* custom variables: 2, 1\.1, True, custom string variable
  \* custom functions: 1 \+ 2 == 3, ECHO
"""  # noqa


@pytest.mark.parametrize("distro,series,codename", [
    ('debian-10', 'buster', 'Buster'),
    ('debian-11', 'bullseye', 'Bullseye'),
    ('debian-12', 'bookworm', 'Bookworm'),
    ('debian-999', 'unstable', 'Sid'),
    ('debian', 'unstable', 'Sid'),
    ('ubuntu-23.10', 'mantic', 'Mantic Minotaur'),
    ('ubuntu-22.04', 'jammy', 'Jammy Jellyfish'),
    ('ubuntu-20.04', 'focal', 'Focal Fossa'),
    ('ubuntu', 'unstable', 'Sid'),
])
def test_template_render(proj, capsys, distro, series, codename):
    """
    test template selection of examples/template-variables
    """
    with cd(proj.path.base):
        assert apkg('srcpkg', '--render-template', '-d', distro) == 0
        out, _ = capsys.readouterr()
        out_path = Path(out.strip()).resolve()
        assert out_path.exists()
        changelog_path = next(out_path.glob('changelog'))
        chl = changelog_path.open('r').read()

    m = re.search(RE_DEB_CH, chl, flags=re.DOTALL)
    assert m
    d_series1, d_series2, d_codename = m.groups()
    assert d_series1 == d_series2

    if series != 'unstable' and d_series1 == 'unstable':
        pytest.skip("distro-info-data not available")
    assert d_series1 == series
    assert d_codename == codename
