from pathlib import Path
import pytest
import re

from apkg.adistro import Distro
from apkg.cli import apkg
from apkg.project import Project
from apkg.util.run import cd
from apkg.util import test


APKG_BASE_DIR = Path(__file__).parents[2]
EXAMPLE_DIR = APKG_BASE_DIR / 'examples/templates'


@pytest.fixture(scope="module")
def repo_path(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("apkg_test_templates_")
    repo_path = test.init_testing_repo(EXAMPLE_DIR, str(tmpdir))
    return repo_path


@pytest.fixture(scope="module")
def proj(repo_path):
    return Project(repo_path.resolve())


@pytest.mark.parametrize("distro,name,style", [
    ('debian-9', 'deb-zzz', 'deb'),
    ('debian-10', 'deb-old', 'deb'),
    ('debian-11', 'deb-old', 'deb'),
    ('debian-12', 'debian-12', 'deb'),
    ('debian-13', 'deb', 'deb'),
    ('debian', 'deb', 'deb'),
    ('Ubuntu 16.04', 'deb-zzz', 'deb'),
    ('ubuntu 20.04', 'deb-old', 'deb'),
    ('ubuntu 22.04', 'ubuntu-22.04', 'deb'),
    ('ubuntu 24.04', 'ubuntu', 'deb'),
    ('ubuntu', 'ubuntu', 'deb'),
    ('rocky-8', 'el-8', 'rpm'),
    ('rocky-9', 'rocky', 'rpm'),
    ('rocky', 'rocky', 'rpm'),
    ('centos-8', 'el-8', 'rpm'),
    ('centos-7', 'rpm', 'rpm'),
    ('CentOS', 'rpm', 'rpm'),
    ('Fedora 38', 'rpm', 'rpm'),
    ('opensuse', 'rpm', 'rpm'),
])
def test_template_select(proj, distro, name, style):
    """
    test template selection of examples/templates
    """
    t = proj.get_template_for_distro(distro)
    assert t.name == name
    assert t.pkgstyle.name == style


RE_RPM_CH = r"""\* \w{3} \w{3} \d{2} \d{4} [^-]+- ([^-]+)-(\w+)
- new upstream version (\S+)
- distro: ([^\n]+)
- include: from shared.txt: apkg-example-templates
- raw include: from shared.txt: {{ name }}\n?(.*)\Z"""


@pytest.mark.parametrize('distro,extra', [
    ('fedora 33', '- Fedora-specific block'),
    ('centos 7', '- only on EL 7 and older'),
    ('rocky 8', '- only on EL 8 (distro alias)'),
    ('rhel 9', ''),
])
def test_template_render_rpm(proj, capsys, distro, extra):
    """
    test rendering of examples/templates/distro/pkg/rpm/*.spec
    """
    with cd(proj.path.base):
        assert apkg('srcpkg', '--render-template', '-d', distro) == 0
        out, _ = capsys.readouterr()
        out_path = Path(out.strip()).resolve()
        assert out_path.exists()
        spec_path = next(out_path.glob('*.spec'))
        spec = spec_path.open('r').read()
        dummy_patch = (out_path / 'dummy.patch').open('r').read()
        copy_only = (out_path / 'COPY_ONLY').open('r').read()
        assert not (out_path / '.ignored_file').exists()

    chl = spec.split('%changelog\n')[-1]
    m = re.search(RE_RPM_CH, chl, flags=re.DOTALL)
    ver, rls, ver2, distro_, extra_ = m.groups()
    assert ver == '1.0'
    assert ver2 == '1.0'
    assert rls == '1'
    d = Distro(distro)
    distro_exp = '%s / %s / %s' % (d, d.idver, d.tiny)
    assert distro_ == distro_exp
    assert extra_.strip() == extra
    assert dummy_patch.strip() == 'No templating: {{ distro }}'
    assert copy_only.strip() == 'No templating: {{ distro }}'


RE_DEB_CH = r"""apkg-example-templates \(([^-]+)-([^)]+)\) unstable; .*
  \* new upstream version (\S+)
  \* distro: ([^\n]+)
  \* include: from shared.txt: apkg-example-templates
  \* raw include: from shared.txt: {{ name }}\n?(.*)
 -- .+?  \w{3}, \d+ \w{3} \d{4} [\d:]{8} [+-]?\d{4}"""


@pytest.mark.parametrize('distro,extra', [
    ('debian-12', '* new Debian-based'),
    ('Debian 11', '* old Debian-based (distro alias)'),
    ('debian-10', '* old Debian-based (distro alias)'),
    ('debian 9', '* ancient Debian-based (distro alias)'),
    ('Ubuntu 22.04', '* new Debian-based'),
    ('Ubuntu 21.04', '* old Debian-based (distro alias)'),
    ('ubuntu-16.04', '* ancient Debian-based (distro alias)'),
    ('LinuxMint', '* only on Linux Mint'),
])
def test_template_render_deb(proj, capsys, distro, extra):
    """
    test rending of examples/templates/distro/pkg/deb/changelog
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
    ver, rls, ver2, distro_, extra_ = m.groups()
    d = Distro(distro)
    assert ver == '1.0'
    assert ver2 == '1.0'
    assert rls == '1~%s' % d.tiny
    distro_exp = '%s / %s / %s' % (d, d.idver, d.tiny)
    assert distro_ == distro_exp
    assert extra_.strip() == extra
