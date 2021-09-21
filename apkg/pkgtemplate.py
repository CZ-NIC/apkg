"""
module for handling and rendering apkg package templates
"""
from pathlib import Path
import re

import jinja2

from apkg.log import getLogger
from apkg import pkgstyle as _pkgstyle
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


DUMMY_ENV = {
    'name': 'PKGNAME',
    'version': '0.VERSION',
    'release': '0.RELEASE',
    'nvr': 'NVR',
    'distro': 'DISTRO',
}


def default_render_filter(path):
    if str(path).endswith('.patch'):
        return False
    return True


class PackageTemplate:
    def __init__(self, path, style=None):
        self.path = Path(path)
        self.style = style

    @property
    def pkgstyle(self):
        if not self.style:
            self.style = _pkgstyle.get_pkgstyle_for_template(self.path)
        return self.style

    def template_env(self, env=None):
        """
        get/update template env from pkgstyle
        """
        # static vars
        tenv = getattr(self.pkgstyle, 'TEMPLATE_ENV', {})
        # dynamic vars resolved at render time
        denv = getattr(self.pkgstyle, 'TEMPLATE_ENV_DYNAMIC', {})
        if denv:
            denv_vars = {}
            for name, fun in denv.items():
                denv_vars[name] = fun()
            tenv.update(denv_vars)
        # custom supplied vars
        if env:
            tenv.update(env)
        return tenv

    def render(self, out_path, env,
               render_filter=default_render_filter,
               includes=None, excludes=None):
        """
        render package template into specified output directory

        Args:
            out_path: output base path
            env: vars available from template
            render_filter: function to determine which files need rendering
            includes: render only files matching these regexes
            excludes: don't render any files matching these regexes
        """
        def is_included(fn):
            if includes:
                for inc_re in includes:
                    if re.match(inc_re, fn):
                        break
                else:
                    return False
            if excludes:
                for exc_re in excludes:
                    if re.match(exc_re, fn):
                        return False
            return True

        log.info("renderding package template: %s -> %s", self.path, out_path)
        if out_path.exists():
            log.verbose("template render dir exists: %s", out_path)
        else:
            out_path.mkdir(parents=True, exist_ok=True)

        env = self.template_env(env=env)

        # recursively render all files
        for d, _, files in shutil.walk(self.path):
            rel_dir = Path(d).relative_to(self.path)
            dst_dir = out_path / rel_dir
            dst_dir.mkdir(parents=True, exist_ok=True)

            for fn in files:
                dst = out_path / rel_dir / fn
                src = Path(d) / fn
                if not is_included(fn):
                    log.verbose("file excluded from render: %s", fn)
                    continue

                # TODO: filtering should be exposed through config
                if render_filter(src):
                    log.verbose("rendering file: %s -> %s", src, dst)
                    t = None
                    with src.open('r') as srcf:
                        t = jinja2.Template(srcf.read())
                    with dst.open('w') as dstf:
                        dstf.write(t.render(**env) + '\n')
                else:
                    log.verbose(
                        "copying file without render: %s -> %s", src, dst)
                    shutil.copyfile(src, dst)
                # preserve original permission
                dst.chmod(src.stat().st_mode)

    def render_file_content(self, name, env):
        """
        render template file in memory and return its content
        """
        src = self.path / name
        env = self.template_env(env=env)
        with src.open('r') as srcf:
            t = jinja2.Template(srcf.read())
        return t.render(**env) + '\n'
