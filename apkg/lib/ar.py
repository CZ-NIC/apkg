"""
apkg lib for handling source archives
"""
import os
from pathlib import Path
import re
import shutil

from apkg import exception
from apkg import log
from apkg.project import Project
from apkg.util.cmd import run


# subgroups:
# 1) name
# 2) name-version separator ('-' or '_')
# 3) version (including release)
RE_NVR = r'^(.+?)([-_])(\d+(?:\.\d+)+(?:.+?)?)$'


def split_archive_fn(archive_fn):
    """
    split archive file name into individual parts
       
    return (name, separator, version, extension)
    """
    nvr, _, ext = archive_fn.rpartition('.')
    ext = '.%s' % ext
    if nvr.endswith('.tar'):
        nvr, _, _ = nvr.rpartition('.')
        ext = '.tar%s' % ext

    r = re.match(RE_NVR, nvr)
    if r:
        return r.groups() + (ext,)

    msg = "unable to parse version from archive file name: %s" % archive_fn
    raise exception.ParsingFailed(msg=msg)


def make_archive(version=None, project=None):
    """
    create archive from current project state
    """
    proj = project or Project()
    try:
        script = proj.config['project']['make_archive_script']
    except KeyError:
        msg = ("make-archive requires project.make_archive_script option to\n"
        "be set in project config to a script that creates project\n"
        "archive and prints path to it on last stdout line.\n\n"
        "Please update project config with required information:\n\n"
        "%s" % proj.config_path)
        raise exception.MissingRequiredConfigOption(msg=msg)

    log.info("running make_archive_script: %s" % script)
    out = run(script)
    # last script stdout line is expected to be path to resulting archive
    _, _, last_line = out.rpartition('\n')
    archive_path = Path(last_line)
    if not archive_path.exists():
        msg = ("make_archive_script finished successfully but the archive\n"
               "(indicated by last script stdout line) doesn't exist:\n\n"
               "%s" % archive_path)
        raise exception.UnexpectedCommandOutput(msg=msg)
    else:
        log.info("archive created: %s" % archive_path)

    archive_fn = archive_path.name
    if version:
        # specific version requested - rename if needed
        name, sep, ver, ext = split_archive_fn(archive_fn)
        if ver != version:
            archive_fn = name + sep + version + ext
            msg = "archive renamed to match requested version: %s"
            log.info(msg, archive_fn)
    out_path = proj.dev_archive_path / archive_fn
    log.info("copying archive to: %s" % out_path)
    os.makedirs(proj.dev_archive_path, exist_ok=True)
    shutil.copy(archive_path, out_path)
    log.success("made archive: %s", out_path)
    return out_path


def get_archive(version=None, project=None):
    raise exception.NotImplemented(
            msg="TODO: get_archive: download upstream archive")


def find_archive(archive, upstream=False, project=None):
    """
    find archive in project path and check/return its version
    """
    ar_path = Path(archive)
    if not ar_path.exists():
        ar_type = archive_type(upstream=upstream)
        if not project:
            project = Project()
        ars = project.find_archives_by_name(archive, upstream=upstream)
        if not ars:
            raise exception.ArchiveNotFound(ar=archive, type=ar_type)
        if len(ars) > 1:
            msg = ("multiple matching %s archives found - "
                   "not sure which one to use:\n" % ar_type)
            for ar in ars:
                msg += "\n%s" % ar
            raise exception.ArchiveNotFound(msg=msg)
        ar_path = Path(ars[0])

        log.verbose("found %s archive: %s", ar_type, ar_path)

    return ar_path


def get_archive_version(archive_path, version=None):
    """
    return archive version detected from archive name

    if version is specified, ensure it matches archive version
    """
    archive_path = Path(archive_path)
    name, sep, ver, ext = split_archive_fn(archive_path.name)
    if version:
        # optional version check requested
        if ver == version:
            log.verbose("archive name matches desired version: %s", version)
        else:
            msg = ("archive name doesn't match desired version: %s\n\n"
                   "desired version: %s\n"
                   "archive version: %s" % (archive_path.name, version, ver))
            raise exception.InvalidVersion(msg=msg)
    else:
        # no version was requested - use archive version
        version = ver
    return version


def archive_type(upstream=False):
    if upstream:
        return 'upstream'
    return 'dev'
