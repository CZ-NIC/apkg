from contextlib import contextmanager
import fnmatch
import hashlib
from pathlib import Path
import sys
import tempfile
from typing import Iterable, Mapping, Optional, Union

from apkg import ex
from apkg.log import getLogger
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


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
        return [copy_paths(p, dst) for p in cache_entry]
    elif isinstance(cache_entry, dict):
        result = {}
        for k, v in cache_entry.items():
            result[k] = copy_paths(v, dst)
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
            print(str(r))
    except TypeError:
        print(str(results))


def print_archive_spec(inspec):
    spec = inspec.copy()

    archive = spec.pop('archive')
    print('archive', archive)

    version = spec.pop('version', None)
    if version is not None:
        print('version', version)

    components = spec.pop('components', {})
    for name, path in components.items():
        print('component:%s' % name, path)

    signatures = spec.pop('signatures', {})
    for name, path in signatures.items():
        if name:
            print('signature:%s' % name, path)
        else:
            print('signature', path)

    assert not spec, "spec contains items we won't be able to parse: %s" % spec


def parse_archive_spec(lines, inputs=None):
    """
    utility to parse apkg input files and input file lists
    into a source package build input specification
    """
    if not lines:
        lines = []
    lines = [line.strip() for line in lines if not line.startswith('#')]

    if not inputs:
        inputs = []
    if len([f for f in inputs if f == '-']) > 1:
        msg = "requested to read stdin multiple times"
        raise ex.ParsingFailed(msg=msg)

    def all_lines():
        yield from lines
        for fl in inputs:
            if fl == '-':
                f = sys.stdin
            else:
                f = open(fl, 'r', encoding='utf-8')

            yield from (ln.strip() for ln in f.readlines()
                        if not ln.startswith('#'))

    result = {}
    for line in all_lines():
        if ' ' not in line:
            msg = ("specification could not be parsed (type missing) "
                   "on line:\n\n"
                   "%s" % line)
            raise ex.ParsingFailed(msg=msg)

        typ, argument, *rest = line.split()
        if rest:
            msg = ("specification could not be parsed on line:\n\n"
                    "%s" % line)
            raise ex.ParsingFailed(msg=msg)

        if typ == "version":
            if "version" in result:
                msg = ("more than one 'version' specified\n")
                raise ex.ParsingFailed(msg=msg)

            result["version"] = argument
            log.info("detected version: %s", argument)
            continue

        in_archive_path = Path(argument)
        if not in_archive_path.exists():
            msg = ("the file listed doesn't exist:\n\n"
                   "%s" % in_archive_path)
            raise ex.ParsingFailed(msg=msg)

        tag, *extra = typ.split(':')

        if tag == "archive":
            if extra:
                msg = ("unexpected tag(s) passed to the 'archive' type: "
                       "%s" % extra)
                raise ex.ParsingFailed(msg=msg)
            if "archive" in result:
                msg = ("more than one 'archive' provided\n")
                raise ex.ParsingFailed(msg=msg)

            result["archive"] = in_archive_path
            log.info("detected archive: %s", in_archive_path)
        elif tag == "signature":
            component = ''
            if extra:
                component = extra[0]

            signatures = result.setdefault("signatures", {})

            if component in signatures:
                if component:
                    msg = ("duplicate signature provided for component "
                           "%s" % component)
                else:
                    msg = "duplicate archive signature provided"
                raise ex.ParsingFailed(msg=msg)

            signatures[component] = in_archive_path
            if component:
                log.success("detected signature for component %r",
                               component)
            else:
                log.success("detected archive signature")
        elif tag == "component":
            if extra:
                component_name = extra[0]
            else:
                component_name, _ = in_archive_path.name.split('.', 1)

            components = result.setdefault("components", {})

            if component_name in components:
                msg = ("duplicate component provided: %s" % component_name)
                raise ex.ParsingFailed(msg=msg)

            components[component_name] = in_archive_path
            log.info("detected component %r: %s", component_name, in_archive_path)
        else:
            msg = ("unrecognised type on line:\n\n"
                   "%s" % line)
            raise ex.ParsingFailed(msg=msg)

    return result


def parse_input_files(files, file_lists):
    """
    utility to parse apkg input files and input file lists
    into a single list of input files
    """
    if not files:
        files = []
    if not file_lists:
        file_lists = []

    all_files = [Path(f) for f in files]

    if len([fl for fl in file_lists if fl == '-']) > 1:
        fail = "requested to read stdin multiple times"
        raise ex.InvalidInput(fail=fail)

    for fl in file_lists:
        if fl == '-':
            f = sys.stdin
        else:
            f = open(fl, 'r', encoding='utf-8')
        all_files += [Path(ln.strip()) for ln in f.readlines()]
        f.close()

    return all_files


def ensure_input_files(infiles):
    if not infiles:
        raise ex.InvalidInput(
            fail="no input file(s) specified")
    if isinstance(infiles, dict):
        for files in infiles.values():
            ensure_input_files(files)
    elif isinstance(infiles, list):
        for f in infiles:
            if isinstance(f, str):
                f = Path(f)
            ensure_input_files(f)
    elif isinstance(infiles, Path) and not infiles.exists():
        raise ex.InvalidInput(fail="input file not found: %s" % infiles)


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
        # NOTE(py35): explicit Path -> str conversion for python 3.5
        with open(str(path), 'rb', buffering=0) as f:
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
