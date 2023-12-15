import re
import requests

from apkg import ex
from apkg.log import getLogger
from apkg.util.upstreamversion import latest_apkg_version


log = getLogger(__name__)


# current apkg compatibility level
COMPAT_LEVEL = 4


COMPAT_LEVEL_NOTES = {
    4: ('0.5.0', """Forward compatible update, no action required."""),
    3: ('0.4.0', """Forward compatible update, no action required."""),
    2: ('0.3.0', """Forward compatible update for most users.

## new flexible template selection mechanism

Make sure each template dir in distro/pkg/ matches name
of a respective pkgstyle such as deb, rpm, arch, or nix.

Inspect new improved `apkg status` package templates listing.""")
}


def ensure_compat(compat_level):
    if not compat_level:
        return
    compat_level = int(compat_level)
    if COMPAT_LEVEL < compat_level:
        raise ex.InvalidCompatLevel(
            proj=compat_level, apkg=COMPAT_LEVEL)


def level_status(compat_level):
    if compat_level is None:
        return False, 'not set'
    elif compat_level < COMPAT_LEVEL:
        return False, 'old'
    elif compat_level > COMPAT_LEVEL:
        return False, 'new'
    elif compat_level == COMPAT_LEVEL:
        return True, 'current'
    else:
        return False, 'error'


def get_level_notes(old_level, new_level=COMPAT_LEVEL):
    """
    return a dict of relevant compat level notes
    for migration from old_level to new_level.
    """
    actions = {}
    for i in range(old_level + 1, new_level + 1):
        actions[i] = COMPAT_LEVEL_NOTES[i]
    return actions


def get_upstream_compat_level(apkg_version=None):
    """
    fetch upstream compat level for apkg version

    use latest version when apkg_version isn't specified
    """
    if not apkg_version:
        apkg_version = latest_apkg_version()

    url = 'https://gitlab.nic.cz/packaging/apkg/-/raw/v%s/apkg/compat.py'
    url = url % apkg_version
    log.verbose("getting upstream compat level for apkg-%s: %s",
                apkg_version, url)

    r = requests.get(url)
    if not r.ok:
        return None
    m = re.search(r'^COMPAT_LEVEL\s*=\s*(\d+)\s*$', r.text, re.MULTILINE)
    if not m:
        return None
    level = int(m.group(1))
    return level
