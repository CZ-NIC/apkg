from pathlib import Path

import click

from apkg import ex
from apkg.cli import cli
from apkg.util import common
from apkg.log import getLogger
from apkg.project import Project
from apkg.util.archive import get_archive_version
from apkg.util.run import run
import apkg.util.shutil35 as shutil


log = getLogger(__name__)

def copy_archive(source, destdir, name=None):
    if name is None:
        name = source.name

    dest = destdir / name

    if source != dest:
        log.info("copying archive to: %s", dest)
        destdir.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, dest)

    return dest


@cli.command(name='make-archive', aliases=['ar'])
@click.option('-O', '--result-dir',
              help="put results into specified dir")
@click.option('--cache/--no-cache', default=True, show_default=True,
              help="enable/distable cache")
@click.help_option('-h', '--help', help='show this help')
def cli_make_archive(*args, **kwargs):
    """
    create dev archive from current project state
    """
    results = make_archive(*args, **kwargs)
    common.print_archive_spec(results)
    return results


def make_archive(
        result_dir=None,
        cache=True,
        project=None):
    """
    create dev archive from current project state

    Use script specified by project.make_archive_script config option.
    """
    log.bold("creating dev archive")
    proj = project or Project()

    use_cache = proj.cache.enabled(
        'source', cmd='make_archive', use_cache=cache)
    if use_cache:
        cache_key = 'archive/dev/%s' % proj.checksum
        cached = common.get_cached_paths(proj, cache_key, result_dir)
        if cached:
            log.success("reuse cached archive: %s", cached['archive'])
            return cached

    script = proj.config_get('project.make_archive_script')
    if not script:
        msg = ("make-archive requires project.make_archive_script option to\n"
               "be set in project config to a script that creates project\n"
               "archive and prints its path to stdout.\n\n"
               "Please update project config with required information:\n\n"
               "%s" % proj.path.config)
        raise ex.MissingRequiredConfigOption(msg=msg)

    log.info("running make_archive_script: %s", script)
    out = run(script, quiet=True)

    lines = out.split('\n')

    if result_dir:
        ar_base_path = Path(result_dir)
    else:
        ar_base_path = proj.path.dev_archive

    if proj.compat_level < 5:
        # Use old undocumented behaviour when the last like of output was used
        in_archive_path = Path(lines[-1])
        archive_path = copy_archive(in_archive_path, ar_base_path)
        results = {'archive': archive_path}
        log.success("made archive: %s", archive_path)
    else:
        try:
            results = common.parse_archive_spec(lines)
        except ex.ParsingFailed as e:
            raise ex.UnexpectedCommandOutput(
                "Failed to parse make-archive output: %s" % e.msg
                ).with_traceback(e.__traceback__)

        if 'archive' not in results:
            msg = "make-archive never provided an archive file"
            raise ex.UnexpectedCommandOutput(msg=msg)

        results = common.copy_paths(results, ar_base_path)

    if "version" not in results:
        results["version"] = get_archive_version(results["archive"])
        log.info("autodetected version %r from archive %s",
                 results["version"], results["archive"])

    if use_cache:
        proj.cache.update(cache_key, results)
    return results


APKG_CLI_COMMANDS = [cli_make_archive]
