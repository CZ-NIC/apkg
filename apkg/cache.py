"""
apkg packaging file cache
"""

import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Union

from apkg import __version__
from apkg.log import getLogger
from apkg.util.common import CacheableEntry, hash_file, hash_path


log = getLogger(__name__)


CacheEntry = Union[str, int, bool, List['CacheEntry'], Dict[str, 'CacheEntry']]


class FileMissingError(Exception):
    pass


class ChecksumError(Exception):
    pass


def file_checksum(*paths) -> str:
    return hash_file(*paths).hexdigest()[:20]


def path_checksum(*paths) -> str:
    return hash_path(*paths).hexdigest()[:20]


def enabled_str(enabled: bool) -> str:
    return 'ENABLED' if enabled else 'DISABLED'


class ProjectCache:
    def __init__(self, project):
        self.project = project
        self.loaded = False
        self.cache = {}
        self.checksum = None

    def save(self) -> None:
        self.cache['__version__'] = __version__
        json.dump(self.cache, self.project.path.cache.open('w'))

    def load(self) -> None:
        cache_path = self.project.path.cache
        if not cache_path.exists():
            log.verbose("cache not found: %s", cache_path)
            return
        log.verbose("loading cache: %s", cache_path)

        cache = json.load(cache_path.open('r'))
        version = cache.get('__version__', None)
        if version != __version__:
            log.verbose("apkg version in cache not ours: %s", version)
            return
        self.cache = cache

    def _ensure_load(self) -> None:
        """
        ensure cache is loaded on demand and only once

        you don't need to call this directly
        """
        if self.loaded:
            return
        self.load()
        self.loaded = True

    def update(self, key: str, entry: CacheableEntry) -> None:
        """
        update cache entry
        """
        log.verbose("cache update: %s -> %s", key, entry)
        assert key
        self._ensure_load()
        self.cache[key] = cache_encode(entry)
        self.save()

    def get(self, key: str) -> CacheableEntry:
        """
        get and validate cache entry or None
        """
        log.verbose("cache query: %s", key)

        assert key
        self._ensure_load()
        entry = self.cache.get(key)
        if not entry:
            return None

        try:
            entry = cache_decode(entry)
        except FileMissingError as e:
            path = e.args[0]
            log.info("invalidating cache for %s due to missing file: %s",
                     key, path)
            self.delete(key)
            return None
        except ChecksumError as e:
            path = e.args[0]
            log.info("invalidating cache for %s due to failed checksum on: %s",
                     key, path)
            self.delete(key)
            path.unlink()
            return None
        return entry

    def delete(self, key: str) -> None:
        """
        delete cache entry
        """
        self.cache.pop(key, None)
        self.save()

    def enabled(self, *targets, cmd: str = None,
                use_cache: bool = True) -> bool:
        """
        helper to tell and log if caching should be enabled

        targets is a list of cache targets that must be enabled:

        * local: cache local files
        * remote: cache remote files
        * source: cache project source (requires VCS)

        optional use_cache utility argument to disable all cache
        """

        def enabled_result(value: bool) -> bool:
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


def cache_encode(entry: CacheableEntry) -> CacheEntry:
    """
    Encode entry for use in cache, suported formats are only:
        - int, bool, str
        - Path (stored with checksum)
        - list if all items are a supported format
        - dict where keys are str, values any supported format
    """
    if isinstance(entry, Mapping):
        result = {}
        for k, v in entry.items():
            if k.startswith('__'):
                raise ValueError(f"Underscore keys are not supported: {k}")
            result[k] = cache_encode(v)
        return result
    elif isinstance(entry, (int, str, bool)):  # str is Iterable
        return entry
    elif isinstance(entry, Iterable):
        return [cache_encode(v) for v in entry]
    elif isinstance(entry, Path):
        return {"path": str(entry), "__hash__": file_checksum(entry)}
    raise NotImplementedError


def cache_decode(entry: CacheEntry) -> CacheableEntry:
    """
    Decode and validate entry from cache, validating existence and checksum of
    path entries along the way.
    """
    if isinstance(entry, dict):
        if '__hash__' in entry:
            path = Path(entry['path'])
            checksum = entry['__hash__']
            if not path.exists():
                raise FileMissingError(path)
            if checksum != file_checksum(path):
                raise ChecksumError(path)
            return path
        return {k: cache_decode(v) for k, v in entry.items()}
    if isinstance(entry, list):
        return [cache_decode(v) for v in entry]
    return entry
