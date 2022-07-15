from contextlib import contextmanager
import fnmatch
import hashlib
from pathlib import Path
import sys
import tempfile

from apkg import ex
from apkg.log import getLogger
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


def copy_paths(paths, dst):
    """
    utility to copy a list of paths to dst
    """
    if not dst.exists():
        dst.mkdir(parents=True, exist_ok=True)
    dst_full = dst.resolve()
    new_paths = []
    for p in paths:
        if p.parent.resolve() == dst_full:
            new_paths.append(p)
        else:
            p_dst = dst / p.name
            log.verbose("copying file: %s -> %s", p, p_dst)
            shutil.copy(p, p_dst)
            new_paths.append(p_dst)
    return new_paths


def get_cached_paths(proj, cache_key, result_dir=None):
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
    for f in infiles:
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
