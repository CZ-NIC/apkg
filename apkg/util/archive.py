"""
apkg archive (tarball) utils
"""
from pathlib import Path
import tempfile

from apkg.parse import split_archive_fn, parse_version
import apkg.util.shutil35 as shutil

from apkg import ex
from apkg.log import getLogger


log = getLogger(__name__)


def unpack_archive(archive_path, out_path):
    """
    unpack supplied archive into out_path dir

    archive is expected to contain a single root dir

    return path to extracted root dir
    """
    out_path = Path(out_path)
    out_path.mkdir(parents=True, exist_ok=True)
    temp_path = Path(tempfile.mkdtemp(
        prefix='temp_', dir=str(out_path)))
    root_files_old = set(temp_path.glob("*"))
    # shutil doesn't provide a way to check extracted files :(
    # pautil has bugs and got last release in 2016...
    shutil.unpack_archive(archive_path, temp_path)
    root_files_new = set(temp_path.glob("*"))
    root_files = root_files_new - root_files_old
    n_root_files = len(root_files)
    if n_root_files != 1:
        fmt = "Expected a single root dir but instead got %d files in root"
        raise ex.InvalidArchiveFormat(fmt=fmt % n_root_files)
    temp_root = root_files.pop()
    out_root = out_path / temp_root.name
    if out_root.exists():
        log.info("removing existing unpacked archive dir: %s", out_root)
        shutil.rmtree(out_root)
    temp_root.rename(out_root)
    return out_root


def get_archive_version(archive_path):
    """
    return archive version detected from archive name
    """
    archive_path = Path(archive_path)
    _, _, ver, _ = split_archive_fn(archive_path.name)
    return parse_version(ver)
