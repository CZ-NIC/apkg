from pathlib import Path
import shutil

import click
import yaml

from apkg import ex
from apkg.cli import cli
from apkg.util import common
from apkg.log import getLogger
from apkg.project import Project
from apkg.util.archive import get_archive_version
from apkg.util.run import run


log = getLogger(__name__)


@cli.command(name='make-archive', aliases=['ar'])
@click.option('-O', '--result-dir',
              help="put results into specified dir")
@click.option('-o', '--out-format', default='yaml', show_default=True,
              type=click.Choice(['yaml', 'list']),
              help="set output format")
@click.option('--cache/--no-cache', default=True, show_default=True,
              help="enable/distable cache")
@click.help_option('-h', '--help', help='show this help')
def cli_make_archive(*args, **kwargs):
    """
    create dev archive from current project state
    """
    out_format = kwargs.pop('out_format')

    results = make_archive(*args, **kwargs)

    if out_format == 'list':
        rlist = archive_dict2list(results)
        common.print_results(rlist)
    else:
        # YAML
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
               "archive and prints its path to stdout in YAML like this:\n\n"
               "archive: pkg/archive/dev/foo-1.2.3.tar.gz\n\n"
               "Please update project config with required information:\n\n"
               "%s" % proj.path.config)
        raise ex.MissingRequiredConfigOption(msg=msg)

    log.info("running make_archive_script: %s", script)
    cmd_out = run(script, quiet=True)
    out = str(cmd_out.stdout)

    if result_dir:
        ar_base_path = Path(result_dir)
    else:
        ar_base_path = proj.path.dev_archive

    results = {}
    if proj.compat_level >= 6:
        try:
            results = yaml.safe_load(out)
        except Exception as e:
            msg = ("Failed to parse make_archive_script YAML output:\n\n"
                   "%s\n\nError:\n\n%s" % (out, e))
            raise ex.UnexpectedCommandOutput(msg=msg)
        if not isinstance(results, dict):
            msg = ("Invalid make_archive_script YAML output format:\n\n"
                   "%s\n\nExpected format example:\n\n"
                   "archive: pkg/archives/dev/foo-1.2.3.tar.gz" % (out))
            raise ex.UnexpectedCommandOutput(msg=msg)
    else:
        # use old undocumented behaviour when the last line of output was used
        msg = ("using legacy make_archive_script format (last line)"
               " due to compat level %s" % proj.compat_level)
        log.info(msg)
        lines = out.split('\n')
        archive_path = Path(lines[-1])
        results["archive"] = archive_path

    sanitize_archive_output(results)

    archive_path = results.get('archive')
    if not archive_path:
        msg="make_archive_script didn't return archive:\n\n%s" % out
        raise ex.UnexpectedCommandOutput(msg=msg)

    # copy all to result dir (updates results in-place)
    copy_archives(results, ar_base_path)

    archive_path = results.get('archive')
    log.success("made archive: %s", archive_path)

    if use_cache:
        proj.cache.update(cache_key, results)
    return results


def sanitize_archive_output(output: dict):
    # convert paths to pathlib.Path
    archive = output.get('archive')
    if archive:
        if not isinstance(archive, Path):
            archive = Path(archive)
            output['archive'] = archive
        if archive and not archive.exists():
            raise ex.ArchiveNotFound(ar=archive)
    components = output.get('components')
    if components:
        for comp_name, comp_path in list(components.items()):
            if not isinstance(comp_path, Path):
                comp_path = Path(comp_path)
                components[comp_name] = comp_path
            if not comp_path.exists():
                raise ex.ArchiveNotFound(
                    msg="Archive component '%s' not found: %s" %
                    (comp_name, comp_path))
    # provide explicit version when possible
    if 'version' not in output and archive:
        output['version'] = get_archive_version(archive)
    # version is always str (can occasionally get int or float)
    version = output.get('version')
    if version and not isinstance(version, str):
        output['version'] = str(version)


def archive_dict2list(output: dict) -> list:
    results = []
    archive = output.get('archive')
    if archive:
        results.append(archive)
    components = output.get('components')
    if components:
        results += components.values()
    return results


def copy_archives(output: dict, destdir: Path):
    """
    copy archive and all components to destdir
    """
    archive = output.get('archive')
    if archive:
        output['archive'] = copy_archive(archive, destdir)
    components = output.get('components')
    if components:
        for comp_name, comp_path in list(components.items()):
            components[comp_name] = copy_archive(
                comp_path, destdir, txt="'%s' component" % comp_name)


def copy_archive(source, destdir, name=None, txt='archive'):
    if name is None:
        name = source.name

    dest = destdir / name

    if source != dest:
        log.info("copying %s to: %s", txt, dest)
        destdir.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, dest)

    return dest


APKG_CLI_COMMANDS = [cli_make_archive]
