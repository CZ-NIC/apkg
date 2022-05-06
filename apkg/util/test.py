"""
shared apkg testing functions
"""
import os
from pathlib import Path

import apkg.util.shutil35 as shutil


def init_testing_repo(repo_path, test_path):
    dst = Path(test_path) / Path(repo_path).name
    inject_tree(repo_path, dst)
    return dst


def inject_tree(src_path, dst_path, ignore_top_dirs=None):
    """
    copy all files from src_path into dst_path

    overwrite existing files including symlinks
    """
    top_ignore = bool(ignore_top_dirs)
    if not dst_path.exists():
        dst_path.mkdir(parents=True, exist_ok=True)

    # recursively copy all files
    for d, subdirs, files in shutil.walk(src_path, topdown=True):
        rel_dir = Path(d).relative_to(src_path)
        dst_dir = dst_path / rel_dir
        dst_dir.mkdir(parents=True, exist_ok=True)

        for fn in files:
            src = Path(d) / fn
            dst = dst_dir / fn
            shutil.copy(src, dst)

        if top_ignore:
            # ignore supplied top dirs
            subdirs[:] = [d for d in subdirs if d not in ignore_top_dirs]
            top_ignore = False

        for sd in subdirs:
            # copy symlinks too
            src = Path(d) / sd
            src_str = str(src)
            if os.path.islink(src_str):
                dst = dst_dir / sd
                if dst.exists():
                    dst.unlink()
                linkto = os.readlink(src_str)
                os.symlink(linkto, dst)


def log_contains(string, caplog):
    for r in caplog.records:
        if string in r.message:
            return True
    return False
