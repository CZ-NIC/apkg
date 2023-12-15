"""
Debian series custom template variables module for apkg.

Parses /usr/share/distro-info/$DISTRO.csv (from distro-info-data package)
to extract distro series (deb_series) and codename (deb_codename).

When no info is found for distro, return "unstable" / "Sid".

Provides custom template variables:

    deb_series : str    (examples: 'bookworm', 'noble', 'unstable')
    deb_codename : str  (examples: 'Bookworm', 'Noble Numbat', 'Sid')

Enable by adding [[template.variables]] entry to distro/config/apkg.toml:

    [[template.variables]]
    python_module = "apkg.templatevars.debseries"

Example usage in debian/chanelog:

    some-package ({{ version }}-{{ release }}~{{ deb_series }}) {{ deb_series }}; urgency=medium

    * upstream package version {{ version }} for {{ distro }} {{ deb_codename }}

    -- Jakub Ružička <jakub.ruzicka@nic.cz>  {{ now }}
"""  # noqa

import csv
from collections import namedtuple


def get_distro_info(distro):
    distro_info_file = '/usr/share/distro-info/%s.csv' % distro
    DistroInfoTuple = None
    info = {}
    try:
        with open(distro_info_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            fields = next(csvreader)
            if not DistroInfoTuple:
                fields = list(map(lambda x: x.replace('-', '_'), fields))
                n_fields = len(fields)
                DistroInfoTuple = namedtuple('DistroInfoTuple', fields)

            for row in csvreader:
                while len(row) < n_fields:
                    row.append(None)
                dit = DistroInfoTuple(*row)
                info[dit.series] = dit
    except Exception:
        return {}

    return info


# called by apkg to get custom variables
def get_variables(env):
    distro_id = env['distro'].id
    distro_version = env['distro'].version
    if distro_version:
        distro_info = get_distro_info(distro_id)
        series_info = None
        for di in distro_info.values():
            # strip LTS and such
            version, _, _ = di.version.partition(' ')
            if distro_id != 'ubuntu':
                # strip minor releases for non-ubuntu (9.2 -> 9)
                version, _, _ = version.partition('.')
            if version == distro_version:
                series_info = di
                break

        if series_info:
            return {
                'deb_series': series_info.series,
                'deb_codename': series_info.codename,
            }

    return {
        'deb_series': 'unstable',
        'deb_codename': 'Sid',
    }
