import pytest

from apkg import adistro


@pytest.mark.parametrize("distro,id,ver", [
    ('arch', 'arch', ''),
    ('debian 10', 'debian', '10'),
    ('Ubuntu 21.04', 'ubuntu', '21.04'),
])
def test_distro_parse(distro, id, ver):
    d = adistro.Distro(distro)
    assert d.id == id
    assert d.version == ver


@pytest.mark.parametrize("rule,distro,match", [
    ('arch', 'arch', True),
    ('debian', 'debian-10', True),
    ('debian > 9', 'debian-10', True),
    ('debian >= 10', 'debian', True),
    ('debian != 10', 'debian', True),
    ('debian <= 10', 'debian', False),
    ('ubuntu <= 18.04', 'ubuntu-20.04', False),
    ('ubuntu == 21.04', 'ubuntu-21.04', True),
])
def test_distro_rule(rule, distro, match):
    r = adistro.DistroRule(rule)
    d = adistro.Distro(distro)
    m = r.match(d)
    assert m == match
    m = d.match(rule)
    assert m == match
