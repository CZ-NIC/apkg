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

    def enabled(self, use_cache=True):
        """
        helper to tell and log if caching is enabled and supported

        optional use_cache argument provided for shared
        argument parsing and logging from apkg.commands
        """
        if use_cache:
            vcs = self.project.vcs
            if vcs:
                log.verbose("%s VCS detected -> cache ENABLED", vcs)
                return True
            else:
                log.verbose("VCS not detected -> cache DISABLED")
        else:
            log.verbose("cache DISABLED")
        return False


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
