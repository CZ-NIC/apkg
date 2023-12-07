import re

from apkg import ex


# subgroups:
# 1) name
# 2) name-version separator ('-' or '_')
# 3) version (including release)
RE_NVR = r'^(.+?)([-_])(v?\d+(?:\.\d+)*(?:.+?)?)$'


def split_archive_ext(archive_fn):
    """
    split archive file into base name and extension such as '.tar.gz'

    return (name, extension)
    """
    name, _, ext = archive_fn.rpartition('.')
    if not name:
        return archive_fn, ''
    ext = '.%s' % ext
    if name.endswith('.tar'):
        name, _, _ = name.rpartition('.')
        ext = '.tar%s' % ext

    return name, ext


def split_archive_fn(archive_fn):
    """
    split archive file name into individual parts

    return (name, separator, version, extension)
    """
    name, ext = split_archive_ext(archive_fn)
    r = re.match(RE_NVR, name)
    if r:
        return r.groups() + (ext,)

    msg = "unable to parse version from archive file name: %s" % archive_fn
    raise ex.ParsingFailed(msg=msg)


def parse_version(version_str):
    """
    parse version from common version strings

    currently only strips v from vX.Y.Z
    """
    if version_str.startswith('v'):
        return version_str[1:]
    return version_str
