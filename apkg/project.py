import glob
import hashlib
from pathlib import Path
import re

import jinja2
import toml
try:
    from functools import cached_property
except ImportError:
    from cached_property import cached_property

from apkg import adistro
from apkg import cache as _cache
from apkg import compat
from apkg import ex
from apkg.log import getLogger
from apkg import pkgtemplate
from apkg import pkgtest
from apkg.util.archive import unpack_archive
from apkg.util.git import git
from apkg.util import upstreamversion


log = getLogger(__name__)


INPUT_BASE_DIR = 'distro'
OUTPUT_BASE_DIR = 'pkg'
CONFIG_FN = 'apkg.toml'


# pylint: disable=too-many-instance-attributes
class ProjectPaths:
    # pylint: disable=redefined-builtin
    def __init__(self, base=None, input=None, output=None):
        self.base = Path(base or '.')
        if input:
            self.input = Path(input)
        else:
            self.input = self.base / INPUT_BASE_DIR
        if output:
            self.output = Path(output)
        else:
            self.output = self.base / OUTPUT_BASE_DIR
        self.update_paths()

    def update_paths(self):
        # project config: distro/config/apkg.toml
        self.config_base = self.input / 'config'
        self.config = self.config_base / CONFIG_FN
        # package templates: distro/pkg
        self.templates = self.input / 'pkg'
        # archives: pkg/archives/{dev,upstream,unpacked}
        self.archive = self.output / 'archives'
        self.dev_archive = self.archive / 'dev'
        self.upstream_archive = self.archive / 'upstream'
        self.unpacked_archive = self.archive / 'unpacked'
        # build: pkg/build/{src-,}pkg
        self.build = self.output / 'build'
        self.package_build = self.build / 'pkgs'
        self.srcpkg_build = self.build / 'srcpkgs'
        # output: pkg/{src-,}pkg
        self.package_out = self.output / 'pkgs'
        self.srcpkg_out = self.output / 'srcpkgs'
        # packaging tests: distro/tests
        self.tests = self.input / 'tests'
        # packaging tests extras: distro/tests/extra
        self.tests_extras = self.tests / 'extra'
        # packaging tests render/run: pkg/tests
        self.tests_out = self.output / 'tests'
        # cache: pkg/.cache.json
        self.cache = self.output / '.cache.json'


class Project:
    """
    Project class serves as high level interface to projecs in need of
    packaging
    """
    name = None
    config = {}
    distro_aliases = {}
    variables_sources = []

    def __init__(
            self,
            base_path=None,
            input_path=None,
            output_path=None,
            auto_load=True,
            auto_compat=True):
        self.auto_compat = auto_compat
        self.cache = _cache.ProjectCache(self)
        self.load_paths(
            base=base_path,
            input=input_path,
            output=output_path)
        if auto_load:
            self.load()

    def load(self):
        """
        load project config and update attributes
        """
        self.load_config()
        self.update_attrs()
        self.update_distro_aliases()
        self.update_variables_sources()
        if self.auto_compat:
            self.ensure_compat()

    def reload(self,
               base_path=None,
               input_path=None,
               output_path=None):
        """
        reload project with new paths supplied
        """
        self.load_paths(
            base=base_path or self.path.base,
            input=input_path or self.path.input,
            output=output_path or self.path.output)
        self.load()

    def load_paths(self, **kwargs):
        self.path = ProjectPaths(**kwargs)

    def load_config(self):
        """
        load project config from file
        """
        if self.path.config.exists():
            log.verbose("loading project config: %s", self.path.config)
            self.config = toml.load(self.path.config.open())
            return True
        else:
            log.verbose("project config not found: %s", self.path.config)
            return False

    def config_get(self, option, default=None):
        """
        get config option if set or default

        example options: 'project.name', 'upstream.archive_url'
        """
        c = self.config
        for key in option.split('.'):
            try:
                c = c[key]
            except KeyError:
                return default
        return c

    def update_attrs(self):
        """
        update project attributes based on current config
        """
        self.name = self.config_get('project.name')
        if self.name:
            log.verbose("project name from config: %s", self.name)
        else:
            self.name = self.path.base.resolve().name
            log.verbose("project name not in config - "
                        "guessing from path: %s", self.name)

    def update_distro_aliases(self):
        """
        load distro aliases from project config
        """
        conf = self.config_get('distro.aliases', [])
        self.distro_aliases = adistro.parse_distro_aliases(conf)

    def update_variables_sources(self):
        """
        load custom variables sources from project config
        """
        conf = self.config_get('template.variables', [])
        self.variables_sources = pkgtemplate.parse_variables_sources(conf)

    @cached_property
    def vcs(self):
        """
        Version Control System used in project

        possible outputs: 'git', None
        """
        o = git('rev-parse', quiet=True, check=False)
        if o.returncode == 0:
            return 'git'
        return None

    @cached_property
    def checksum(self):
        """
        checksum of current project state

        requires VCS (git), only computed once
        """
        if self.vcs == 'git':
            checksum = git.current_commit()[:10]
            diff = git('diff', quiet=True)
            if diff:
                diff_hash = hashlib.sha256(diff.encode('utf-8'))
                checksum += '-%s' % diff_hash.hexdigest()[:10]
            return checksum
        return None

    @property
    def compat_level(self):
        """
        current project compat level as set in config
        """
        return self.config_get('apkg.compat')

    def ensure_compat(self):
        compat.ensure_compat(self.compat_level)

    def upstream_archive_url(self, version):
        url = self.config_get('upstream.archive_url')
        if not url:
            return None
        tvars = {'project': self, 'version': version}
        url = jinja2.Template(url).render(**tvars)
        return url

    def upstream_signature_url(self, version):
        url = self.config_get('upstream.signature_url')
        if not url:
            return None
        tvars = {'project': self, 'version': version}
        url = jinja2.Template(url).render(**tvars)
        return url

    @cached_property
    def upstream_version(self):
        """
        check latest upstream version

        upstream is only queried once

        possible outputs: version, None
        """
        uv_script = self.config_get('upstream.version_script')
        if uv_script:
            v = upstreamversion.version_from_script(
                uv_script, script_name='upstream.version_script')
            log.info("detected upstream version (from script): %s", v)
            return v
        ar_url = self.upstream_archive_url('VERSION')
        if ar_url:
            m = re.match(r'(.*/)[^/]+', ar_url)
            ar_base_url = m.group(1)
            v = upstreamversion.version_from_listing(ar_base_url)
            log.info("detected upstream version: %s", v)
            return v
        return None

    @cached_property
    def templates(self):
        if self.path.templates.exists():
            ignore_files = self.config_get('template.ignore_files')
            plain_copy_files = self.config_get('template.plain_copy_files')
            return pkgtemplate.load_templates(
                self.path.templates,
                distro_aliases=self.distro_aliases,
                ignore_files=ignore_files,
                plain_copy_files=plain_copy_files,
                variables_sources=self.variables_sources)
        else:
            return []

    def get_template_for_distro_(self, distro):
        for t in self.templates:
            if t.match_distro(distro):
                return t
        return None

    def get_template_for_distro(self, distro):
        if not isinstance(distro, adistro.Distro):
            distro = adistro.Distro(distro)
        template = self.get_template_for_distro_(distro)
        if not template:
            tdir = self.path.templates
            msg = ("missing package template for distro: %s\n\n"
                   "you can add it into: %s" % (distro.idver, tdir))
            raise ex.MissingPackagingTemplate(msg=msg)
        return template

    def load_upstream_archive(self, ar_path):
        """
        load project config from --upstream archive
        """
        unpack_path = unpack_archive(ar_path, self.path.unpacked_archive)
        input_path = unpack_path / 'distro'
        log.info("reloading project from upstream archive: %s", unpack_path)
        # reload project with input_path from archive
        self.reload(input_path=input_path)

    @cached_property
    def tests_extras(self):
        if self.path.tests_extras.exists():
            return pkgtest.load_tests_extras(
                self.path.tests_extras,
                distro_aliases=self.distro_aliases)
        else:
            return []

    def get_tests_extra_for_distro(self, distro):
        for e in self.tests_extras:
            if e.match_distro(distro):
                return e
        return None

    def get_tests_for_distro(self, distro):
        extra = self.get_tests_extra_for_distro(distro)
        tests = pkgtest.PackageTests(
            tests_in_path=self.path.tests,
            tests_out_path=self.path.tests_out,
            extra=extra,
            distro=distro)
        return tests

    def find_archives_by_name(self, name, upstream=False):
        """
        find archive files with supplied name in expected project paths
        """
        if upstream:
            ar_path = self.path.upstream_archive
        else:
            ar_path = self.path.dev_archive
        return glob.glob("%s/%s*" % (ar_path, name))
