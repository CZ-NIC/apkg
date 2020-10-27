"""
show status of current project

usage: apkg status
"""

from docopt import docopt
import distro
import os

from apkg import log
from apkg.project import Project
from apkg import pkgstyle


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    print_status()


def print_status():
    proj = Project()

    msg = "project base path:       {t.bold}{path}{t.normal}"
    print(msg.format(path=proj.path.resolve(), t=log.T))

    msg = "project config:          {t.bold}{path}{t.normal}"
    if proj.config_path.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.warn}doesn't exist{t.normal})"
    print(msg.format(path=proj.config_path, t=log.T))

    msg = "package templates path:  {t.bold}{path}{t.normal}"
    if proj.package_templates_path.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.red}doesn't exist{t.normal})"
    print(msg.format(path=proj.package_templates_path, t=log.T))

    print("package templates:")
    if proj.package_templates:
        msg_lines = []
        for template in proj.package_templates:
            short_path = os.path.join(*list(template.path.parts)[-3:])
            msg_lines.append("    {t.green}%s{t.normal}: {t.bold}%s{t.normal}"
                    % (template.package_style.name, short_path))
        msg = "\n".join(msg_lines)
    else:
        msg = "    {t.red}no package templates found{t.normal}"
    print(msg.format(dir=proj.package_templates_path, t=log.T))

    print()
    # distro status
    msg = "current distro: {t.cyan}{full}{t.normal} ({t.cyan}{id}{t.normal})"
    distro_full = " ".join(distro.linux_distribution()).rstrip()
    distro_id = distro.id()
    print(msg.format(full=distro_full, id=distro_id, t=log.T))

    msg = "    package style: "
    style = pkgstyle.get_package_style_for_distro(distro_id)
    if style:
        msg += "{t.green}%s{t.normal}" % style.name
    else:
        msg += "{t.warn}unsupported{t.normal}"
    print(msg.format(t=log.T))