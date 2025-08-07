from contextlib import contextmanager
import fnmatch
import hashlib
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Iterable, Mapping, Optional, Union

import yaml

from apkg import ex
from apkg.log import getLogger


log = getLogger(__name__)


PATH_FORMAT = 'relative'


CacheableEntry = Union[str, int, bool, Path,
                       Iterable['CacheableEntry'],
                       Mapping[str, 'CacheableEntry']]


def copy_paths(cache_entry: CacheableEntry, dst: Path) -> CacheableEntry:
    """
    utility to copy a list of paths to dst
    """
    if not dst.exists():
        dst.mkdir(parents=True, exist_ok=True)
    dst_full = dst.resolve()

    if isinstance(cache_entry, Path):
        if cache_entry.parent.resolve() != dst_full:
            p_dst = dst / cache_entry.name
            log.verbose("copying file: %s -> %s", cache_entry, p_dst)
            shutil.copy(cache_entry, p_dst)
            return p_dst
        return cache_entry
    elif isinstance(cache_entry, list):
        return [copy_paths(p) for p in cache_entry]
    elif isinstance(cache_entry, dict):
        result = {}
        for k, v in cache_entry.items():
            result[k] = copy_paths(v)
        return result
    return cache_entry


def get_cached_paths(proj, cache_key: str,
                     result_dir: Optional[str] = None) -> CacheableEntry:
    """
    get cached files and move them to result_dir if specified
    """
    paths = proj.cache.get(cache_key)
    if not paths:
        return None
    if result_dir:
        paths = copy_paths(paths, Path(result_dir))
    return paths


def print_results(results):
    """
    print results received from apkg command
    """
    try:
        for r in results:
            print(format_path(r))
    except TypeError:
        print(str(results))


def print_results_dict(results):
    """
    print results dict as YAML (used in make-archive and get-archive)
    """
    print(yaml_dump(results))


def format_path(path: Path):
    if PATH_FORMAT == 'absolute':
        return str(path.absolute())
    elif PATH_FORMAT == 'stem':
        return str(path.stem)
    return str(path)


def yaml_path_representer(dumper, obj):
    # to print pathlib.Path as str
    return dumper.represent_scalar("tag:yaml.org,2002:str", format_path(obj))


class SafeDumper(yaml.dumper.SafeDumper):
    # don't modify global PyYAML state
    pass


yaml.add_representer(
    # print pathlib.Path as str
    type(Path()),
    yaml_path_representer,
    SafeDumper,
)


def yaml_dump(*args, **kwargs):
    kwargs['Dumper'] = SafeDumper
    return yaml.dump(*args, **kwargs).rstrip()


def parse_inputs(inputs, in_files, in_format='list'):
    """
    utility parser of apkg command inputs
    """
    all_inputs = list(inputs) if inputs else []

    if in_files:
        if len([fl for fl in in_files if fl == '-']) > 1:
            fail = "requested to read stdin multiple times"
            raise ex.InvalidInput(fail=fail)

        for fl in in_files:
            if fl == '-':
                f = sys.stdin
            else:
                f = open(fl, 'r', encoding='utf-8')
            all_inputs += [ln.rstrip() for ln in f.readlines()]
            f.close()

    if in_format == 'yaml':
        result = parse_yaml_inputs(all_inputs)
    else:
        result = parse_list_inputs(all_inputs)

    return result


def parse_list_inputs(inputs):
    return [Path(i) for i in inputs]


def parse_yaml_inputs(inputs):
    if not inputs:
        return {}
    txt = '\n'.join(inputs)
    result = yaml.safe_load(txt)
    return result


def ensure_inputs(inputs, n=0):
    if not inputs:
        raise ex.InvalidInput(
            fail="no input file specified")
    if n:
        n_in = len(inputs)
        if n_in != n:
            exp = 'single input file' if n == 1 else '%s input files' % n
            ins = '\n'.join([str(p) for p in inputs])
            raise ex.InvalidInput(
                fail="expected %s, but got %s:\n\n%s" % (exp, n_in, ins))
    for f in inputs:
        if not f or not f.exists():
            raise ex.InvalidInput(
                fail="input file not found: %s" % f)


@contextmanager
def text_tempfile(text, prefix='apkg_tmp_'):
    """
    write text to a new temporary file and return its path

    file is deleted after use
    """
    f = tempfile.NamedTemporaryFile(
        prefix=prefix, mode='w+t', delete=False)
    path = Path(f.name)
    f.write(text)
    f.close()
    try:
        yield path
    finally:
        path.unlink()


def hash_file(*paths, algo='sha256'):
    """
    return hashlib's hash computed over the contents of the specified file

    typical use case: `hash_file('/path').hexdigest()`
    """
    # code based on https://stackoverflow.com/a/44873382/587396
    h = getattr(hashlib, algo)()
    b = bytearray(128*1024)
    mv = memoryview(b)
    for path in paths:
        with open(path, 'rb', buffering=0) as f:
            while True:
                # NOTE: pylint's cell-var-from-loop cries made me do this >:(
                n = f.readinto(mv)
                if n == 0:
                    break
                h.update(mv[:n])
    return h


def hash_path(*paths, algo='sha256'):
    """
    return hashlib's hash computed over the supplied file paths (as strings)

    typical use case: `hash_path('/path').hexdigest()`
    """
    h = getattr(hashlib, algo)()
    for path in paths:
        h.update(str(path).encode('utf-8'))
    return h


def fnmatch_any(filename, patterns):
    """
    check if a filename matches any of supplied patterns
    """
    for p in patterns:
        if fnmatch.fnmatch(filename, p):
            return True
    return False


def serialize(obj):
    if isinstance(obj, (list, tuple)):
        return [serialize(v) for v in obj]
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, (str, bool, int, float)):
        return obj
    return str(obj)


class SortReversor:
    """
    use this with multi-key sort() to reverse individual keys
    """
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj


def sanitize_fn(name):
    """
    sanitize a string to be safe for use as a filename
    """
    return re.sub(r'[\\/\\:*?"\'<>| ]', '_', name)


def set_path_format(fmt: str) -> str:
    """
    set global path format
    """
    global PATH_FORMAT

    if not fmt or 'relative'.startswith(fmt):
        PATH_FORMAT = 'relative'
    elif 'absolute'.startswith(fmt):
        PATH_FORMAT = 'absolute'
    elif 'stem'.startswith(fmt):
        PATH_FORMAT = 'stem'
    else:
        raise ex.InvalidFormat(
            msg="Invalid path format: %s" % fmt)


def get_path_format():
    """
    set global path format
    """
    return PATH_FORMAT
