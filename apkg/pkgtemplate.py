"""
module for handling and rendering apkg package templates
"""
from collections import UserDict
import glob
import importlib.util
import os

from pathlib import Path
import jinja2
import jinja2.ext
from markupsafe import Markup

from apkg import ex
from apkg import adistro
from apkg.log import getLogger
from apkg import pkgstyle as _pkgstyle
from apkg.pkgstyle import call_pkgstyle_fun
from apkg.util import common
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


DUMMY_VARS = {
    'name': 'PKGNAME',
    'version': '0.VERSION',
    'release': '0.RELEASE',
    'nvr': 'NAME-VERSION-RELEASE',
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


class IncludeRawExtension(jinja2.ext.Extension):
    """
    custom jinja tag include_raw to insert file contents without templating

    Usage from template:

        {% include_raw 'distro/pkg/foo' %}
    """
    tags = {"include_raw"}

    def parse(self, parser):
        lineno = parser.stream.expect("name:include_raw").lineno
        fn = jinja2.nodes.Const(parser.parse_expression().value)
        result = self.call_method("_render", [fn], lineno=lineno)
        return jinja2.nodes.Output([result], lineno=lineno)

    def _render(self, filename):
        src = self.environment.loader.get_source(self.environment, filename)[0]
        return Markup(src.rstrip('\n'))


# pylint: disable=too-many-instance-attributes
class PackageTemplate:
    def __init__(self, path, style=None, selection=TS_DISTRO,
                 ignore_files=None, plain_copy_files=None,
                 variables_sources=None):
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
        self.variables_sources = variables_sources

        self.setup_env()

    def setup_env(self):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('.'),
            extensions=[IncludeRawExtension])

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
        get/update template variables
        """
        vars_ = DUMMY_VARS.copy()

        # package name from template
        name = call_pkgstyle_fun(
            self.pkgstyle, 'get_template_name', self.path)
        vars_['name'] = name
        # static pkgstyle vars
        vars_pkgstyle = getattr(self.pkgstyle, 'TEMPLATE_VARS', {})
        vars_.update(vars_pkgstyle)
        # dynamic pkgstyle vars resolved at render time
        vars_dyn = getattr(self.pkgstyle, 'TEMPLATE_VARS_DYNAMIC', {})
        if vars_dyn:
            for name, fun in vars_dyn.items():
                vars_[name] = fun()
        # supplied vars
        if tvars:
            vars_.update(tvars)
        # custom variables
        if self.variables_sources:
            vars_ = self.custom_vars(vars_)

        return vars_

    def custom_vars(self, tvars):
        """
        get/update template variables from custom sources
        """
        for vsrc in self.variables_sources:
            vsrc.validate()
            log.info("custom variables from %s: %s",
                     vsrc.src_attr, vsrc.src_val)
            custom_tvars = vsrc.get_variables(tvars)
            log.verbose("%s custom variables: %s",
                        len(custom_tvars), custom_tvars)
            tvars.update(custom_tvars)

        return tvars

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
        for d, _, files in shutil.walk(self.path, followlinks=True):
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
                   plain_copy_files=None,
                   variables_sources=None):
    """
    load package templates sorted by evaluation priority

    Params:
        path - templates base path (i.e.: distro/pkg)
        distro_aliases - distro aliases dict (optional)
        ignore_files - list of file patterns to ignore (optional)
        plain_copy_files - list of file patterns to copy
                           without templating (optional)
        variables_sources - list of sources to define
                            template variables (optional)

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
            plain_copy_files=plain_copy_files,
            variables_sources=variables_sources)

        if not template.pkgstyle:
            log.warning("ignoring unknown package style in %s", entry_path)
            continue

        alias_rules = aliases.get(template.name)
        if alias_rules:
            # distro alias template (name match)
            template.selection = TS_ALIAS
            template.distro_rules = alias_rules
            alias_tps.append(template)
            continue

        dstyle = _pkgstyle.PKGSTYLES.get(template.name)
        if dstyle:
            # pkgstyle default template (name match)
            template.selection = TS_PKGSTYLE
            rules = adistro.distro_rules(dstyle.SUPPORTED_DISTROS)
            template.distro_rules = rules
            pkgstyle_tps.append(template)
            continue

        # distro-specific template
        template.distro_rules = adistro.name2rule(template.name)
        distro_tps.append(template)

    alias_tps = sort_alias_templates(alias_tps, distro_aliases)
    distro_tps = adistro.sort_by_name(distro_tps)
    pkgstyle_tps.sort(key=lambda x: x.name)
    templates = alias_tps + distro_tps + pkgstyle_tps
    return templates


def sort_alias_templates(alias_templates, distro_aliases):
    result = []
    for da in distro_aliases:
        for at in alias_templates:
            if at.name == da:
                result.append(at)
                break
    assert len(alias_templates) == len(result)
    return result


class VariablesSource(UserDict):
    VARS_SOURCES = ['local_module', 'python_module']

    def __init__(self, **kwargs):
        super().__init__(kwargs)

    @property
    def local_module(self):
        return self.get('local_module', None)

    @property
    def python_module(self):
        return self.get('python_module', None)

    @property
    def src_attr(self):
        for src in self.VARS_SOURCES:
            if src in self.data:
                return src
        return None

    @property
    def src_val(self):
        return self.data.get(self.src_attr, None)

    def validate(self):
        src_attrs = [src for src in self.VARS_SOURCES if self.get(src)]
        n_src = len(src_attrs)
        if n_src < 1:
            raise ex.InvalidVariablesSource(
                src="no source specified: %s" % self)
        if n_src > 1:
            raise ex.InvalidVariablesSource(
                src="multiple conflicting sources: %s" % self)
        return True

    def exists(self):
        if self.src_attr == 'local_module':
            return Path(self.local_module).exists()
        elif self.src_attr == 'python_module':
            try:
                spec = importlib.util.find_spec(self.python_module)
                return spec is not None
            except ModuleNotFoundError:
                return False
        else:
            return False

    def get_variables(self, tvars):
        if self.local_module:
            if not os.path.exists(self.local_module):
                raise ex.InvalidVariablesSource(
                    src='local_module not found: %s' % (self.local_module))

            spec = importlib.util.spec_from_file_location(
                "custom_variables", self.local_module)

            custom_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(custom_module)
        elif self.python_module:
            try:
                custom_module = importlib.import_module(self.python_module)
            except ModuleNotFoundError:
                raise ex.InvalidVariablesSource(
                    src='python_module not found: %s' % self.python_module)

        custom_fun = getattr(custom_module, 'get_variables', None)
        if not custom_fun:
            raise ex.InvalidVariablesSource(
                src='%s missing required get_variables function: %s'
                % (self.src_val, custom_module))

        custom_tvars = custom_fun(tvars)
        return custom_tvars


def parse_variables_sources(config):
    sources = []
    for vcfg in config:
        vsrc = VariablesSource(**vcfg)
        sources.append(vsrc)
    return sources
