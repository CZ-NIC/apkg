"""
generate docs from apkg code/docstrings using mkdocs-macros-plugin
"""
import inspect
import re
import subprocess

from apkg.compat import COMPAT_LEVEL
from apkg import ex
from apkg import pkgstyle
from apkg import pkgtemplate
from pathlib import Path


BASE_PATH = Path(__file__).parent.parent
BASE_CODE_URL = "https://gitlab.nic.cz/packaging/apkg/-/blob/master/"
APKG_NEW_ISSUE_URL = "https://gitlab.nic.cz/packaging/apkg/-/issues/new"


def define_env(env):
    """
    this is available in docs using jinja2 templates
    """
    env.variables.compat_level = COMPAT_LEVEL
    env.variables.exceptions = get_exceptions()
    env.variables.new_issue_url = APKG_NEW_ISSUE_URL
    env.variables.pkgstyles = pkgstyle.PKGSTYLES
    env.variables.pkgtemplate = pkgtemplate

    @env.filter
    def relpath(path):
        return Path(path).relative_to(BASE_PATH)

    @env.filter
    def file_link(path):
        fn = Path(path)
        try:
            # full path can be passed (i.e. on Read the Docs)
            fn = Path(path).relative_to(BASE_PATH)
        except ValueError:
            pass
        return "[{fn}]({url}{fn})".format(
            fn=fn,
            url=BASE_CODE_URL)

    @env.filter
    def file_raw(path):
        return Path(path).open('r').read().strip()

    @env.filter
    def file_text(path):
        text = Path(path).open('r').read().strip()
        return "``` text\n%s\n```" % text

    @env.filter
    def mod_doc(modname):
        mod = __import__(modname, fromlist=[''])
        return mod.__doc__.strip()

    @env.filter
    def run(cmd):
        out = subprocess.getoutput(cmd)
        return "``` text\n$> %s\n\n%s\n```" % (
            cmd, out)

    @env.filter
    def cmd_help(cmd):
        c = 'apkg %s --help' % cmd
        return run(c)

    @env.macro
    def added_in_version(version, compat=None, extra=None, action='Added'):
        vlink = 'news.md#apkg-%s' % link_id(version)
        md = '!!! info\n    %s in `apkg` [%s](%s)' % (action, version, vlink)
        if compat:
            compat = str(compat)
            clink = 'news.md#compat-level-%s-news' % link_id(compat)
            md += ', compat level [%s](%s) ([?](compat.md))' % (compat, clink)
        if extra:
            md += ' ' + extra
        return md


def get_exceptions():
    """
    return all apkg exceptions sorted by returncode
    """
    exs = [e for _, e in inspect.getmembers(ex, inspect.isclass)]
    exs.sort(key=lambda x: x.returncode)
    return exs


def link_id(s):
    """
    return HTML id string for linking
    """
    return re.sub(r'[\W]+', '', s)
