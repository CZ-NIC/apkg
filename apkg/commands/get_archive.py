from pathlib import Path
import re
import requests

import click

from apkg import ex
from apkg.util import common
from apkg.log import getLogger
from apkg.project import Project


log = getLogger(__name__)


@click.command(name='get-archive')
@click.option('-v', '--version',
              help='version of archive to download')
@click.option('-O', '--result-dir',
              help="put results into specified dir")
@click.option('--cache/--no-cache', default=True, show_default=True,
              help="enable/distable cache")
@click.help_option('-h', '--help', help='show this help')
def cli_get_archive(*args, **kwargs):
    """
    download upstream archive for current project
    """
    results = get_archive(*args, **kwargs)
    common.print_results(results)
    return results


def get_archive(
        version=None,
        result_dir=None,
        cache=True,
        project=None):
    """
    download upstream archive for current project

    upstream.archive_url config option specifies archive to download.

    If upstream.signature_url config option is provided,
    target signature file is downloaded alongside the archive.

    When no --version is specified, apkg tries to detect latest version:

    1) using upstream.version_script if set
    2) from HTML listing if upstream.archive_url is set
    """
    proj = project or Project()
    if not version:
        version = proj.upstream_version
        if not version:
            raise ex.UnableToDetectUpstreamVersion()
    archive_url = proj.upstream_archive_url(version)

    use_cache = proj.cache.enabled(
        'remote', cmd='get_archive', use_cache=cache)
    if use_cache:
        cache_key = 'archive/upstream/%s' % archive_url
        cached = common.get_cached_paths(proj, cache_key, result_dir)
        if cached:
            log.success("reuse cached archive: %s", cached[0])
            return cached

    log.info('downloading archive: %s', archive_url)

    _, _, archive_fn = archive_url.rpartition('/')
    if result_dir:
        ar_base_path = Path(result_dir)
    else:
        ar_base_path = proj.path.upstream_archive

    r = requests.get(archive_url, allow_redirects=True)
    if r.status_code != 200:
        raise ex.FileDownloadFailed(code=r.status_code, url=archive_url)
    content_type = r.headers.get('content-type', '')
    if not content_type.startswith('application/'):
        msg = 'Failed to download archive - invalid content-type "%s":\n\n%s'
        raise ex.FileDownloadFailed(
            msg=msg % (content_type, archive_url))

    content_disp = r.headers.get('content-disposition')
    if content_disp:
        m = re.search(r'filename=(.+)', content_disp)
        if m:
            archive_fn = m.group(1).strip(' "')
            log.verbose("archive file name from HTTP Content-Disposition: %s",
                        archive_fn)

    archive_path = ar_base_path / archive_fn
    log.info('saving archive to: %s', archive_path)
    ar_base_path.mkdir(parents=True, exist_ok=True)
    archive_path.open('wb').write(r.content)
    log.success('downloaded archive: %s', archive_path)
    results = [archive_path]

    signature_url = proj.upstream_signature_url(version)
    if signature_url:
        # singature check
        log.info('downloading signature: %s', signature_url)
        r = requests.get(signature_url, allow_redirects=True)
        if not r.ok:
            raise ex.FileDownloadFailed(
                code=r.status_code, url=signature_url)
        _, _, signature_name = signature_url.rpartition('/')
        signature_path = ar_base_path / signature_name
        log.info('saving signature to: %s', signature_path)
        signature_path.open('wb').write(r.content)
        log.success('downloaded signature: %s', signature_path)
        results.append(signature_path)
    else:
        log.verbose("project.upstream_signature_url not set"
                    " - skipping signature download")

    if use_cache:
        proj.cache.update(cache_key, results)

    return results


def parse_archive_args(proj, archive, upstream, infiles):
    """
    Helper to parse archive arguments,
    use get-archive,
    and reload project config from archive
    as appropriate.

    Useful for other commands.
    """
    archive_files = infiles
    if upstream:
        archive = True
        if not archive_files:
            archive_files = get_archive(project=proj)
    if archive:
        common.ensure_input_files(archive_files)
        proj.load_upstream_archive(archive_files[0])
    return archive, archive_files


APKG_CLI_COMMANDS = [cli_get_archive]
