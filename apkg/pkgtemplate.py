"""
module for handling and rendering apkg package templates
"""
import glob
import os

from pathlib import Path
from packaging import version
import jinja2

from apkg import adistro
from apkg.log import getLogger
from apkg import pkgstyle as _pkgstyle
from apkg.util import common
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


DUMMY_VARS = {
    'name': 'PKGNAME',
    'version': '0.VERSION',
    'release': '0.RELEASE',
    'nvr': 'NVR',
    'distro': 'DISTRO',
}

# package template selection types ordered by priority
TS_ALIAS, TS_DISTRO, TS_PKGSTYLE = range(3)
TEMPLATE_SELECTION_STR = {
    TS_ALIAS: 'distro alias',
    TS_DISTRO: 'distro-specific',
    TS_PKGSTYLE: 'pkgstyle default',
}

DEFAULT_IGNORE_FILES = [
    '.*',
]
DEFAULT_PLAIN_COPY_FILES = [
    '*.patch',
]


# pylint: disable=too-many-instance-attributes
class PackageTemplate:
    def __init__(self, path, style=None, selection=TS_DISTRO,
                 ignore_files=None, plain_copy_files=None):
        self.path = Path(path)
        self.style = style
        self.selection = selection
        self.distro_rules = None

        if ignore_files is None:
            self.ignore_files = DEFAULT_IGNORE_FILES
        else:
            self.ignore_files = ignore_files
        if plain_copy_files is None:
            self.plain_copy_files = DEFAULT_PLAIN_COPY_FILES
        else:
            self.plain_copy_files = plain_copy_files

        self.setup_env()

    def setup_env(self):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('.'))

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, val):
        self._path = Path(val)
        self._name = self._path.name

    @property
    def name(self):
        return self._name

    @property
    def pkgstyle(self):
        if not self.style:
            self.style = _pkgstyle.get_pkgstyle_for_template(self.path)
        return self.style

    def selection_str(self):
        return TEMPLATE_SELECTION_STR.get(self.selection, 'INVALID')

    def match_distro(self, distro):
        return self.distro_rules.match(distro)

    def template_vars(self, tvars=None):
        """
        get/update template variables from pkgstyle
        """
        # static pkgstyle vars
        result = getattr(self.pkgstyle, 'TEMPLATE_VARS', {})
        # dynamic pkgstyle vars resolved at render time
        tvars_dyn = getattr(self.pkgstyle, 'TEMPLATE_VARS_DYNAMIC', {})
        if tvars_dyn:
            _vars = {}
            for name, fun in tvars_dyn.items():
                _vars[name] = fun()
            result.update(_vars)
        # custom supplied vars
        if tvars:
            result.update(tvars)
        return result

    def render(self, out_path, tvars):
        """
        render package template into specified output directory

        Args:
            out_path: output base path
            tvars: variables available from template
        """
        log.info("renderding package template: %s -> %s", self.path, out_path)
        if out_path.exists():
            log.verbose("template render dir exists: %s", out_path)
        else:
            out_path.mkdir(parents=True, exist_ok=True)

        tvars = self.template_vars(tvars=tvars)

        # recursively render all files
        for d, _, files in shutil.walk(self.path):
            rel_dir = Path(d).relative_to(self.path)
            dst_dir = out_path / rel_dir
            dst_dir.mkdir(parents=True, exist_ok=True)

            for fn in files:
                dst = out_path / rel_dir / fn
                src = Path(d) / fn
                if common.fnmatch_any(fn, self.ignore_files):
                    log.verbose("ignoring template file: %s", src)
                    continue

                if common.fnmatch_any(fn, self.plain_copy_files):
                    log.verbose(
                        "plain copying file without render: %s -> %s",
                        src, dst)
                    shutil.copyfile(src, dst)
                else:
                    log.verbose("rendering file: %s -> %s", src, dst)
                    t = self.env.get_template(str(src))
                    with dst.open('w') as dstf:
                        dstf.write(t.render(**tvars) + '\n')

                # preserve original permission
                dst.chmod(src.stat().st_mode)

    def render_file_content(self, name, tvars):
        """
        render template file in memory and return its content
        """
        src = self.path / name
        tvars = self.template_vars(tvars=tvars)
        t = self.env.get_template(str(src))
        return t.render(**tvars) + '\n'

    def __repr__(self):
        return "PackageTemplate<%s,%s>" % (self.name, self.pkgstyle.name)


def load_templates(path,
                   distro_aliases=None,
                   ignore_files=None,
                   plain_copy_files=None):
    """
    load package templates sorted by evaluation priority

    Params:
        path - templates base path (i.e.: distro/pkg)
        distro_aliases - distro aliases dict (optional)
        ignore_files - list of file patterns to ignore (optional)
        plain_copy_files - list of file patterns to copy
                           without templating (optional)

    Returns:
        list of PackageTemplates in order they should
        be evaluated (by selection type):

        1) distro alias templates
        2) distro-specific templates
        3) pkgstyle default templates
    """
    alias_tps = []
    distro_tps = []
    pkgstyle_tps = []

    aliases = distro_aliases or {}

    for entry_path in glob.glob('%s/*' % path):
        if not os.path.isdir(entry_path):
            # ignore non-dirs
            continue

        template = PackageTemplate(
            entry_path,
            ignore_files=ignore_files,
            plain_copy_files=plain_copy_files)

        if not template.pkgstyle:
            log.warning("ignoring unknown package style in %s", entry_path)
            continue

        dstyle = _pkgstyle.PKGSTYLES.get(template.name)
        if dstyle:
            # pkgstyle default template (name match)
            template.selection = TS_PKGSTYLE
            rules = adistro.distro_rules(dstyle.SUPPORTED_DISTROS)
            template.distro_rules = rules
            pkgstyle_tps.append(template)
            continue

        alias_rules = aliases.get(template.name)
        if alias_rules:
            # distro alias template (name match)
            template.selection = TS_ALIAS
            template.distro_rules = alias_rules
            alias_tps.append(template)
            continue

        # distro-specific template
        template.distro_rules = distro_template_rules(template.name)
        distro_tps.append(template)

    distro_tps = sort_distro_templates(distro_tps)
    alias_tps.sort(key=lambda x: x.name)
    pkgstyle_tps.sort(key=lambda x: x.name)
    templates = alias_tps + distro_tps + pkgstyle_tps
    return templates


def distro_template_rules(name):
    """
    return distro rules based on distro-specific template name
    """
    rule_str, _, ver = name.partition('-')
    if ver:
        rule_str += ' == %s' % ver
    return adistro.DistroRule(rule_str)


def sort_distro_templates(dts):
    """
    sort distro templates by evaluation priority

    Params:
        dts: list of distro templates (PackageTemplate)

    Return:
        same list ordered by priority:

        * specific templates that include release first
        * secondary sort by release desc (for determinism)
    """

    def sort_key(t):
        distro, _, rls = t.name.rpartition('-')
        rlsv = version.parse(rls)
        return distro, common.SortReversor(rlsv)

    plain_dts = []
    rls_dts = []
    for t in dts:
        if '-' in t.name:
            rls_dts.append(t)
        else:
            plain_dts.append(t)

    rls_dts.sort(key=sort_key)
    plain_dts.sort(key=lambda x: x.name)

    return rls_dts + plain_dts
