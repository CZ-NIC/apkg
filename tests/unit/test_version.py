import pytest

from apkg import parse


@pytest.mark.parametrize("fn,ver", [
    ('a-0.xz', '0'),
    ('B_1.zip', '1'),
    ('foo-20232323.tar.gz', '20232323'),
    ('foo-bar-1.2.3.tar.xz', '1.2.3'),
    ('foo_bar_baz_1.0post1.tar.xz', '1.0post1'),
    ('foo-bar_20dev0+deadbee.tar.bz', '20dev0+deadbee'),
    ('foo_bar-01.002.0003.tar.gz2', '01.002.0003'),
])
def test_version_parse(fn, ver):
    _, _, version, _ = parse.split_archive_fn(fn)
    assert version == ver
