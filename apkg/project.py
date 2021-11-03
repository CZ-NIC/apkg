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
from apkg.util.git import git
from apkg.util import upstreamversion


log = getLogger(__name__)


INPUT_BASE_DIR = 'distro'
OUTPUT_BASE_DIR = 'pkg'
CONFIG_FN = 'apkg.toml'


# pylint: disable=too-many-instance-attributes
# TODO: consider moving paths to project.path.* to address this warning
class Project:
    """
    Project class serves as high level interface to projecs in need of
    packaging
    """
    config = {}
    distro_aliases = {}

    name = None
    path = None
    templates_path = None
    cache_path = None
    config_base_path = None
    config_path = None
    archive_path = None
    dev_archive_path = None
    upstream_archive_path = None
    unpacked_archive_path = None
    build_path = None
    package_build_path = None
    srcpkg_build_path = None
    package_out_path = None
    srcpkg_out_path = None

    def __init__(self, path=None, auto_load=True, auto_compat=True):
        if path:
            self.path = path
        else:
            self.path = Path('.')
        if auto_load:
            self.load()
        if auto_compat:
            self.ensure_compat()
        self.cache = _cache.ProjectCache(self)

    def load(self,
             input_path=None,
             output_path=None):
        """
        load project config and update attributes
        """
        if not input_path:
            input_path = self.path / INPUT_BASE_DIR
        self.input_path = input_path

        if not output_path:
            output_path = self.path / OUTPUT_BASE_DIR
        self.output_path = output_path

        self.config_base_path = self.input_path / 'config'
        self.config_path = self.config_base_path / CONFIG_FN
        self.load_config()
        self.update_attrs()
        self.update_paths()
        self.update_distro_aliases()

    def load_config(self):
        """
        load project config from file
        """
        if self.config_path.exists():
            log.verbose("loading project config: %s", self.config_path)
            self.config = toml.load(self.config_path.open())
            return True
        else:
            log.verbose("project config not found: %s", self.config_path)
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
            self.name = self.path.resolve().name
            log.verbose("project name not in config - "
                        "guessing from path: %s", self.name)

    def update_paths(self):
        """
        fill in projects paths based on current self.path and self.config
        """
        # package templates: distro/pkg
        self.templates_path = self.input_path / 'pkg'
        # archives: pkg/archives/{dev,upstream,unpacked}
        self.archive_path = self.output_path / 'archives'
        self.dev_archive_path = self.archive_path / 'dev'
        self.upstream_archive_path = self.archive_path / 'upstream'
        self.unpacked_archive_path = self.archive_path / 'unpacked'
        # build: pkg/build/{src-,}pkg
        self.build_path = self.output_path / 'build'
        self.package_build_path = self.build_path / 'pkgs'
        self.srcpkg_build_path = self.build_path / 'srcpkgs'
        # output: pkg/{src-,}pkg
        self.package_out_path = self.output_path / 'pkgs'
        self.srcpkg_out_path = self.output_path / 'srcpkgs'
        # cache: pkg/.cache.json
        self.cache_path = self.output_path / '.cache.json'

    def update_distro_aliases(self):
        """
        load distro aliases from project config
        """
        conf = self.config_get('distro.aliases', [])
        self.distro_aliases = adistro.parse_distro_aliases(conf)

    @cached_property
    def vcs(self):
        """
        Version Control System used in project

        possible outputs: 'git', None
        """
        o = git('rev-parse', silent=True, fatal=False)
        if o.return_code == 0:
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
            diff = git('diff', log_cmd=False)
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
        if self.templates_path.exists():
            ignore_files = self.config_get('template.ignore_files')
            plain_copy_files = self.config_get('template.plain_copy_files')
            return pkgtemplate.load_templates(
                self.templates_path,
                distro_aliases=self.distro_aliases,
                ignore_files=ignore_files,
                plain_copy_files=plain_copy_files)
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
            tdir = self.templates_path
            msg = ("missing package template for distro: %s\n\n"
                   "you can add it into: %s" % (distro.idver, tdir))
            raise ex.MissingPackagingTemplate(msg=msg)
        return template

    def find_archives_by_name(self, name, upstream=False):
        """
        find archive files with supplied name in expected project paths
        """
        if upstream:
            ar_path = self.upstream_archive_path
        else:
            ar_path = self.dev_archive_path
        return glob.glob("%s/%s*" % (ar_path, name))
