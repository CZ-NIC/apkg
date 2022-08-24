"""
module for running apkg packaging tests
"""
import email
import glob
import os
import re

from pathlib import Path
try:
    from functools import cached_property
except ImportError:
    from cached_property import cached_property

import jinja2

from apkg import adistro
from apkg import ex
from apkg.log import getLogger
from apkg import pkgstyle as _pkgstyle
from apkg.pkgtemplate import IncludeRawExtension
from apkg.util.run import run, sudo
from apkg.util.test import inject_tree
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


# tests extra selection types ordered by priority
TES_ALIAS, TES_DISTRO, TES_PKGSTYLE, TES_ALL = range(4)
TESTS_EXTRA_SELECTION_STR = {
    TES_ALIAS: 'distro alias',
    TES_DISTRO: 'distro-specific',
    TES_PKGSTYLE: 'pkgstyle default',
    TES_ALL: 'default fallback',
}


class TestConfig:
    def __init__(self,
                 name=None,
                 test_command=None,
                 tests_dir=None,
                 deps=None,
                 restrictions=None):
        self.name = name
        self.test_command = test_command
        self.tests_dir = tests_dir
        self.deps = deps if deps else []
        self.restrictions = restrictions if restrictions else []

    def __str__(self):
        if self.test_command:
            return '$ %s' % self.test_command
        return self.name


def parse_test_config(test_text):
    tests = []
    deps = []
    restrictions = []

    msg = email.message_from_string(test_text)
    tests_text = msg['Tests']
    test_command_text = msg['Test-Command']
    tests_dir = msg['Tests-Directory']
    if tests_dir:
        tests_dir = Path(tests_dir)
    deps_text = msg['Depends']
    restrictions_text = msg['Restrictions']

    if deps_text:
        deps = re.split(r'[\s\n]*,[\s\n]*', deps_text.strip())
        # @ means "all packages built from source package"
        # this is implicit with apkg tests
        deps = [d for d in deps if d and d != '@']

    if restrictions_text:
        restrictions = re.split(r'[\s\n]+', restrictions_text.strip())

    if not (tests_text or test_command_text):
        log.warning("Test missing both Tests and Test-Command fields"
                    " - skipping. Test text:\n%s", test_text)
        return tests

    if test_command_text:
        tc = TestConfig(
            test_command=test_command_text,
            tests_dir=tests_dir,
            deps=deps,
            restrictions=restrictions,
        )
        tests.append(tc)

    if tests_text:
        for tn in re.split(r'[\s\n,]+', tests_text.strip()):
            tc = TestConfig(
                name=tn,
                tests_dir=tests_dir,
                deps=deps,
                restrictions=restrictions,
            )
            tests.append(tc)

    return tests


class TestsExtra:
    def __init__(self, path,
                 selection=TES_DISTRO,
                 distro_rules=None):
        self.path = path
        self.selection = selection
        self.distro_rules = distro_rules

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

    @cached_property
    def control_path(self):
        return self._path / 'control'

    @cached_property
    def has_extra_files(self):
        for f in self._path.iterdir():
            if f.name == 'control':
                continue
            return True
        return False

    def selection_str(self):
        return TESTS_EXTRA_SELECTION_STR.get(self.selection, 'INVALID')

    def match_distro(self, distro):
        return self.distro_rules.match(distro)

    @cached_property
    def env(self):
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader('.'),
            extensions=[IncludeRawExtension])

    def render(self, out_path, tvars):
        """
        render tests extra files into specified output directory

        Args:
            out_path: output base path
            tvars: variables available from extra templates
        """
        log.info("renderding tests extra: %s -> %s", self.path, out_path)
        if out_path.exists():
            log.verbose("tests extra output dir exists: %s", out_path)
        else:
            out_path.mkdir(parents=True, exist_ok=True)

        # recursively render all files
        for d, _, files in shutil.walk(self.path, followlinks=True):
            rel_dir = Path(d).relative_to(self.path)
            dst_dir = out_path / rel_dir
            dst_dir.mkdir(parents=True, exist_ok=True)

            for fn in files:
                dst = out_path / rel_dir / fn
                src = Path(d) / fn

                log.verbose("rendering tests extra file: %s -> %s", src, dst)
                t = self.env.get_template(str(src))
                with dst.open('w') as dstf:
                    dstf.write(t.render(**tvars))

                # preserve original permission
                dst.chmod(src.stat().st_mode)

    def render_file_content(self, name, tvars):
        """
        render tests extra file in memory and return its content
        """
        src = self.path / name
        t = self.env.get_template(str(src))
        return t.render(**tvars)

    def __repr__(self):
        return "TestsExtra<%s>" % self.name


class PackageTests:
    def __init__(self, tests_in_path, tests_out_path, extra, distro):
        self.tests_in_path = tests_in_path
        self.tests_out_path = tests_out_path
        self.tests_path = tests_in_path
        self.control_path = tests_in_path / 'control'
        self.distro = distro
        self.extra = extra
        self.extra_control = False
        if self.extra and self.extra.control_path.exists():
            self.control_path = self.extra.control_path
            self.extra_control = True

    @cached_property
    def tvars(self):
        """
        vars availabe during templating
        """
        return {
            'distro': self.distro,
        }

    @property
    def extra_path(self):
        if not self.extra:
            return None
        return self.extra.path

    @cached_property
    def control_text(self):
        if self.extra_control:
            return self.extra.render_file_content(
                'control', self.tvars)
        if not self.control_path.exists():
            return ''
        return self.control_path.open('rt').read().strip()

    @cached_property
    def tests(self):
        tests = []
        if not self.control_text:
            return []
        for txt in re.split(r'\n\s*\n[\s\n]*', self.control_text.strip()):
            tests.extend(parse_test_config(txt))
        return tests

    @cached_property
    def deps(self):
        d = set()
        for tc in self.tests:
            for dep in tc.deps:
                d.add(dep)
        return sorted(d)

    def prepare(self):
        """
        prepare packaging tests for run
        """
        if self.extra and self.extra.has_extra_files:
            # extra with overlay files - need to copy over
            self.tests_path = self.tests_out_path / self.distro.idver / 'tests'
            log.info("preparing tests instance with extra files: %s -> %s",
                     self.tests_in_path, self.tests_path)
            if self.tests_path.exists():
                log.verbose("removing existing tests instance: %s",
                            self.tests_path)
                shutil.rmtree(self.tests_path)
            else:
                self.tests_path.parent.mkdir(exist_ok=True, parents=True)
            inject_tree(self.tests_in_path, self.tests_path,
                        ignore_top_dirs=['extra'])
            self.extra.render(self.tests_path, self.tvars)
            return

        # inline tests (no overlay files from extra)
        log.info("using inline tests: %s", self.tests_path)
        self.tests_path = self.tests_in_path

    def filter_tests(self, test_filter):
        if not test_filter:
            return self.tests
        return [t for t in self.tests if re.search(test_filter, str(t))]

    def run(self, test_filter=None):
        """
        run packaging tests
        """
        self.prepare()
        n_all_tests = len(self.tests)
        if n_all_tests < 1:
            msg = "No tests found in: %s" % self.tests_path
            raise ex.InvalidUsage(msg=msg)
        tests = self.filter_tests(test_filter)
        if test_filter:
            log.info("filtering tests by regex: %s", test_filter)
            if not tests:
                msg = "No tests match regex filter: %s" % test_filter
                raise ex.InvalidUsage(msg=msg)
        n_tests = len(tests)
        log.info("running %s of %s tests...",
                 n_tests, n_all_tests)

        tests_ok = []
        tests_fail = []
        tests_skip = []
        for tc in tests:
            shell = False
            if tc.name:
                tests_path = tc.tests_dir or self.tests_path
                cmd = str(tests_path / tc.name)
            elif tc.test_command:
                cmd = tc.test_command
                shell = True
            else:
                log.warning("skipping invalid test")
                continue

            log.bold("test RUN: %s", cmd)
            try:
                if 'needs-root' in tc.restrictions:
                    _run = sudo
                else:
                    _run = run
                out = _run(cmd, shell=shell, check=False,
                           log_fun=log.verbose_command)
                if out.returncode == 77:
                    log.warning("test SKIP: %s (exit code: %s)",
                                cmd, out.returncode)
                    tests_skip.append(tc)
                elif out.returncode != 0:
                    if 'flaky' in tc.restrictions:
                        log.warning("test SKIP FLAKY: %s (exit code: %s)",
                                    cmd, out.returncode)
                        tests_skip.append(tc)
                    else:
                        log.error("test FAIL: %s (exit code: %s)",
                                  cmd, out.returncode)
                        tests_fail.append(tc)
                else:
                    log.success("test OK: %s", cmd)
                    tests_ok.append(tc)
            except ex.CommandNotFound:
                log.error("test FAIL: %s (command not found)", cmd)
                tests_fail.append(tc)

        if tests_fail:
            log.error("%s tests failed", len(tests_fail))
            return False
        if not tests_ok:
            log.error("no tests were run")
            return False
        if tests_skip:
            log.success("%s tests succeeded, %s skipped",
                        len(tests_ok), len(tests_skip))
        else:
            log.success("%s tests succeeded", len(tests_ok))

        return True


def load_tests_extras(path, distro_aliases=None):
    """
    load package tests' extras sorted by evaluation priority

    Params:
        path - tests extras base path (i.e.: distro/tests/extra)
        distro_aliases - distro aliases dict (optional)

    Returns:
        list of TestsExtras in order of evaluation
    """
    aliases = distro_aliases or {}

    alias_exs = []
    distro_exs = []
    pkgstyle_exs = []
    default_ex = None

    for entry_path in glob.glob('%s/*' % path):
        if not os.path.isdir(entry_path):
            # ignore non-dirs
            continue

        extra = TestsExtra(entry_path)

        alias_rules = aliases.get(extra.name)
        if alias_rules:
            # distro alias (name match)
            extra.selection = TES_ALIAS
            extra.distro_rules = alias_rules
            alias_exs.append(extra)
            continue

        dstyle = _pkgstyle.PKGSTYLES.get(extra.name)
        if dstyle:
            # pkgstyle default (name match)
            extra.selection = TES_PKGSTYLE
            extra.distro_rules = adistro.distro_rules(dstyle.SUPPORTED_DISTROS)
            pkgstyle_exs.append(extra)
            continue

        if extra.name == 'all':
            # default fallback (special 'all' name)
            extra.selection = TES_ALL
            extra.distro_rules = adistro.DistroRuleAll()
            default_ex = extra
            continue

        # distro-specific
        extra.distro_rules = adistro.name2rule(extra.name)
        distro_exs.append(extra)

    distro_exs = adistro.sort_by_name(distro_exs)
    alias_exs.sort(key=lambda x: x.name)
    pkgstyle_exs.sort(key=lambda x: x.name)
    extras = alias_exs + distro_exs + pkgstyle_exs
    if default_ex:
        extras.append(default_ex)

    return extras
