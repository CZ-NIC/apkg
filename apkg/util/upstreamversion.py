# -*- encoding: utf-8 -*-

import re

import bs4
from packaging import version
import requests
import yaml

from apkg import ex
from apkg.log import getLogger
from apkg.util.run import run


log = getLogger(__name__)


RE_ARCHIVE_VERSION = r'[\w-]+-(\d[^-]+)\.tar\..*'


def version_from_script(script, script_name='script', proj=None):
    """
    get version from a script
    """
    log.verbose("getting upstream version from %s: %s", script_name, script)
    out = run(script, quiet=True)
    if proj and proj.compat_level < 6:
        # use old behaviour - the last line of output was used
        msg = ("using legacy %s format (last line)"
               " due to compat level %s" % (script_name, proj.compat_level))
        log.warning(msg)
        _, _, last_line = out.rpartition('\n')
        v = last_line.strip()
    else:
        # modern YAML output (compat >= 6)
        try:
            results = yaml.safe_load(out)
        except Exception as e:
            msg = ("Failed to parse %s YAML output:\n\n"
                   "%s\n\nError:\n\n%s" % (script_name, out, e))
            raise ex.UnexpectedCommandOutput(msg=msg)
        if not isinstance(results, dict) or 'version' not in results:
            msg = ("Invalid %s YAML output format:\n\n"
                   "%s\n\nExpected format example:\n\n"
                   "version: 1.2.3" % (script_name, out))
            raise ex.UnexpectedCommandOutput(msg=msg)
        v = results['version']
    v = version.parse(v)
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
