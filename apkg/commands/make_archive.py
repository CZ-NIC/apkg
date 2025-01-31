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
    common.print_results_dict(results)
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

    results = {}
    if proj.compat_level < 6:
        # Use old undocumented behaviour when the last line of output was used
        in_archive_path = Path(lines[-1])
        archive_path = copy_archive(in_archive_path, ar_base_path)
        results["archive"] = archive_path
        log.success("made archive: %s", archive_path)
    else:
        for line in lines:
            if line.startswith('#'):
                continue

            typ, argument, *rest = line.split()
            if rest:
                msg = ("make_archive_script finished successfully but\n"
                       "output could not be parsed on line:\n\n"
                       "%s" % line)
                raise ex.UnexpectedCommandOutput(msg=msg)

            if typ == "version":
                if "version" in results:
                    msg = ("make_archive_script returned more than one "
                           "'version'\n")
                    raise ex.UnexpectedCommandOutput(msg=msg)

                results["version"] = argument
                log.success("detected version: %s", argument)
                continue

            in_archive_path = Path(argument)
            if not in_archive_path.exists():
                msg = ("make_archive_script finished successfully but\n"
                       "the file listed doesn't exist:\n\n"
                       "%s" % in_archive_path)
                raise ex.UnexpectedCommandOutput(msg=msg)

            tag, *extra = typ.split(':')

            if tag == "archive":
                if "archive" in results:
                    msg = ("make_archive_script returned more than one "
                           "'archive'\n")
                    raise ex.UnexpectedCommandOutput(msg=msg)

                archive_path = copy_archive(in_archive_path, ar_base_path)
                results["archive"] = archive_path
                log.success("made archive: %s", archive_path)
            elif tag == "component":
                if extra:
                    component_name = extra[0]
                else:
                    component_name, _ = in_archive_path.name.split('.', 1)

                components = results.setdefault("components", {})

                if component_name in components:
                    msg = ("make_archive_script returned a duplicate\n"
                           "component:\n\n"
                           "%s" % component_name)
                    raise ex.UnexpectedCommandOutput(msg=msg)

                archive_path = copy_archive(in_archive_path, ar_base_path)
                components[component_name] = archive_path
                log.success("made archive for component %r: %s",
                            component_name, archive_path)
            else:
                msg = ("make_archive_script returned an unknown tag\n"
                       "on line:\n\n"
                       "%s" % line)

    if "version" not in results:
        results["version"] = get_archive_version(results["archive"])

    if use_cache:
        proj.cache.update(cache_key, results)
    return results


def copy_archive(source, destdir, name=None):
    if name is None:
        name = source.name

    dest = destdir / name

    if source != dest:
        log.info("copying archive to: %s", dest)
        destdir.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, dest)

    return dest


APKG_CLI_COMMANDS = [cli_make_archive]
