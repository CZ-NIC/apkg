"""
This is convenience interface to apkg.pkgstyles.* modules which can be
dynamically added because apkg.pkgstyles is PEP 420 namespace package.
"""
import importlib
import pkgutil

from apkg import ex
from apkg.log import getLogger
import apkg.pkgstyles


log = getLogger(__name__)


def iter_pkgstyles():
    return pkgutil.iter_modules(
        apkg.pkgstyles.__path__,
        apkg.pkgstyles.__name__ + ".")


def import_pkgstyles():
    styles = {}
    for _, modname, _ in iter_pkgstyles():
        _, _, name = modname.rpartition('.')
        module = importlib.import_module(modname)
        # insert package style name into module for convenience
        module.name = name
        styles[name] = module
    return styles


def get_pkgstyle_for_template(path):
    for style in PKGSTYLES.values():
        if style.is_valid_template(path):
            return style
    return None


def get_pkgstyle_for_distro(distro):
    for style in PKGSTYLES.values():
        for sup_distro in style.SUPPORTED_DISTROS:
            if distro.id.startswith(sup_distro):
                return style
    return None


def get_pkgstyle(style):
    return PKGSTYLES.get(style)


def ensure_pkgstyle_fun(pkgstyle, fun):
    f = getattr(pkgstyle, fun, None)
    if not f:
        msg = "%s pkgstyle is missing required function: %s"
    elif not callable(f):
        msg = "%s pkgstyle error: not a function: %s"
    else:
        return f
    raise ex.DistroNotSupported(
        msg % (pkgstyle.__name__, fun))


def call_pkgstyle_fun(pkgstyle, fun, *args, **kwargs):
    f = ensure_pkgstyle_fun(pkgstyle, fun)
    log.verbose("calling %s function: %s", pkgstyle.__name__, fun)
    return f(*args, **kwargs)


PKGSTYLES = import_pkgstyles()
