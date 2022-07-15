from pathlib import Path

import click

from apkg import ex
from apkg.cli import cli
from apkg.util import common
from apkg.log import getLogger
from apkg.project import Project
from apkg.util.run import run
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


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
    common.print_results(results)
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
            log.success("reuse cached archive: %s", cached[0])
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
    # last script stdout line is expected to be path to resulting archive
    _, _, last_line = out.rpartition('\n')
    in_archive_path = Path(last_line)
    if not in_archive_path.exists():
        msg = ("make_archive_script finished successfully but the archive\n"
               "(indicated by last script stdout line) doesn't exist:\n\n"
               "%s" % in_archive_path)
        raise ex.UnexpectedCommandOutput(msg=msg)
    log.info("archive created: %s", in_archive_path)

    if result_dir:
        ar_base_path = Path(result_dir)
    else:
        ar_base_path = proj.path.dev_archive
    archive_fn = in_archive_path.name
    archive_path = ar_base_path / archive_fn
    if archive_path != in_archive_path:
        log.info("copying archive to: %s", archive_path)
        ar_base_path.mkdir(parents=True, exist_ok=True)
        shutil.copy(in_archive_path, archive_path)
    log.success("made archive: %s", archive_path)
    results = [archive_path]
    if use_cache:
        proj.cache.update(cache_key, results)
    return results


APKG_CLI_COMMANDS = [cli_make_archive]
