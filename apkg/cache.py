"""
apkg packaging file cache
"""

import json
from pathlib import Path

from apkg.log import getLogger
from apkg.util.common import hash_file, hash_path


log = getLogger(__name__)


def file_checksum(*paths):
    return hash_file(*paths).hexdigest()[:20]


def path_checksum(*paths):
    return hash_path(*paths).hexdigest()[:20]


def enabled_str(enabled):
    return 'ENABLED' if enabled else 'DISABLED'


class ProjectCache:
    def __init__(self, project):
        self.project = project
        self.loaded = False
        self.cache = {}
        self.checksum = None

    def save(self):
        json.dump(self.cache, self.project.path.cache.open('w'))

    def load(self):
        cache_path = self.project.path.cache
        if not cache_path.exists():
            log.verbose("cache not found: %s", cache_path)
            return
        log.verbose("loading cache: %s", cache_path)
        self.cache = json.load(cache_path.open('r'))

    def _ensure_load(self):
        """
        ensure cache is loaded on demand and only once

        you don't need to call this directly
        """
        if self.loaded:
            return
        self.load()
        self.loaded = True

    def update(self, key, paths):
        """
        update cache entry
        """
        log.verbose("cache update: %s -> %s", key, paths[0])
        assert key
        self._ensure_load()
        entries = list(map(path2entry, paths))
        self.cache[key] = entries
        self.save()

    def get(self, key):
        """
        get cache entry or None
        """
        log.verbose("cache query: %s", key)

        def validate(path, checksum):
            if not path.exists():
                log.info("removing missing file from cache: %s", path)
                self.delete(key)
                return False
            real_checksum = file_checksum(path)
            if real_checksum != checksum:
                log.info("removing invalid cache entry: %s", path)
                self.delete(key)
                return False
            return True

        def entry2path_valid(e):
            return entry2path(e, validate_fun=validate)

        assert key
        self._ensure_load()
        entries = self.cache.get(key)
        if not entries:
            return None
        paths = list(map(entry2path_valid, entries))
        if None in paths:
            # invalid entry
            return None
        return paths

    def delete(self, key):
        """
        delete cache entry
        """
        self.cache.pop(key, None)
        self.save()

    def enabled(self, *targets, cmd=None, use_cache=True):
        """
        helper to tell and log if caching should be enabled

        targets is a list of cache targets that must be enabled:

        * local: cache local files
        * remote: cache remote files
        * source: cache project source (requires VCS)

        optional use_cache utility argument to disable all cache
        """

        def enabled_result(value):
            en_str = enabled_str(value)
            if cmd:
                log.verbose("cache %s for %s", en_str, cmd)
            else:
                log.verbose("cache %s", en_str)
            return value

        if not use_cache:
            # all cache disabled
            return enabled_result(use_cache)

        r = True
        for target in targets:
            option = 'cache.%s' % target
            value = self.project.config_get(option)
            cache = True

            if value is not None:
                # set in project config
                if value and target == 'source' and not self.project.vcs:
                    # source cache requires VCS
                    msg = ("cache.{target} {en} in project config, "
                           "but VCS isn't available - cache.{target} {di}.\n"
                           "Please update your project config.").format(
                        target=target,
                        en=enabled_str(value),
                        di=enabled_str(False))
                    log.warning(msg)
                    cache = False
                else:
                    log.verbose("cache.%s %s in project config",
                                target, enabled_str(value))
                    cache = value

            else:
                # auto cache settings
                if target == 'source':
                    # source cache requires VCS
                    cache = bool(self.project.vcs)
                    log.verbose("cache.%s %s by default (VCS=%s)",
                                target, enabled_str(cache), self.project.vcs)
                else:
                    # other cache types are ENABLED by default
                    log.verbose("cache.%s %s by default",
                                target, enabled_str(True))

            # always go through all targets to get complete logs
            r = r and cache

        return enabled_result(r)


def path2entry(path):
    """
    convert a path to corresponding cache entry

    return (fn, checksum) or a list of that on multiple paths
    """
    return str(path), file_checksum(path)


def entry2path(entry, validate_fun=None):
    """
    convert cache entry to a corresponding path

    if validate_fun is specified, it's used confirm file has
    valid checksum and flush invalid cache entry if it doesn't
    """
    fn, checksum = entry
    p = Path(fn)
    if validate_fun:
        if not validate_fun(p, checksum):
            return None
    return p
