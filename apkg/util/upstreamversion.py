# -*- encoding: utf-8 -*-

import re

import bs4
from packaging import version
import requests

from apkg.log import getLogger
from apkg.util.run import run


log = getLogger(__name__)


RE_ARCHIVE_VERSION = r'[\w-]+-(\d[^-]+)\.tar\..*'


def version_from_script(script, script_name='script'):
    """
    get version from last stdout line of a script
    """
    log.verbose("getting upstream version from %s: %s", script_name, script)
    out = run(script, quiet=True)
    _, _, last_line = out.rpartition('\n')
    v = version.parse(last_line.strip())
    return v


def version_from_listing(html_listing_url):
    """
    get latest version from HTML listing
    """
    log.verbose("getting upstream version from HTML listing: %s",
                html_listing_url)
    found = False
    v_max = version.parse('0')
    r = requests.get(html_listing_url)
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    for a in soup.find_all('a'):
        m = re.match(RE_ARCHIVE_VERSION, a.string)
        if not m:
            continue
        v_str = m.group(1)
        try:
            v = version.parse(v_str)
        except version.InvalidVersion:
            log.verbose("Ignoring invalid upstream version: %s in %s",
                        v_str, a.string)
            continue
        v_max = max(v, v_max)
        found = True
    if found:
        return v_max
    return None


def version_from_pypi(name):
    """
    get latest version from PyPI by name
    """
    log.verbose("getting upstream version from PyPI: %s", name)
    url = 'https://pypi.org/pypi/%s/json' % name
    r = requests.get(url)
    if not r.ok:
        return None
    data = r.json()

    versions = data['releases'].keys()
    ver = sorted(versions, key=version.parse)[-1]

    return ver


def latest_apkg_version():
    return version_from_pypi('apkg')
