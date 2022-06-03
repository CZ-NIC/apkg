import click

from apkg import adistro
from apkg.cli import cli
from apkg.commands.get_archive import parse_archive_args
from apkg.commands.test_dep import test_dep as cmd_test_dep
from apkg import ex
from apkg.log import getLogger, T
from apkg.project import Project
from apkg.util import common


log = getLogger(__name__)


@cli.command(name="test", aliases=['tests'])
@click.argument('input_files', nargs=-1)
@click.option('-i', '--info', is_flag=True,
              help="show tests information and exit")
@click.option('-l', '--list-tests', is_flag=True,
              help="list tests and exit")
@click.option('-c', '--show-control', is_flag=True,
              help="print tests control file and exit (render if needed)")
@click.option('-u', '--upstream', is_flag=True,
              help="use upstream archive")
@click.option('-a', '--archive', is_flag=True,
              help="use test deps from archive")
@click.option('-d', '--distro',
              help="override target distro  [default: current]")
@click.option('-t', '--test-dep', is_flag=True,
              help="install testing dependencies on host (apkg test-dep)")
@click.option('-k', '--test-filter',
              help="only select tests matching supplied REGEX")
@click.option('-F', '--file-list', 'input_file_lists', multiple=True,
              help=("specify text file listing one input file per line"
                    ", use '-' to read from stdin"))
@click.help_option('-h', '--help',
                   help="show this help message")
def cli_test(*args, **kwargs):
    """
    run packaging tests
    """
    r = test(*args, **kwargs)
    if not r:
        raise ex.PkgTestFail


def test(
        info=False,
        list_tests=False,
        show_control=False,
        upstream=False,
        archive=None,
        input_files=None,
        input_file_lists=None,
        distro=None,
        test_dep=False,
        test_filter=None):
    """
    run packaging tests
    """
    proj = Project()
    distro = adistro.distro_arg(distro, proj)
    infiles = common.parse_input_files(input_files, input_file_lists)
    archive, archive_files = parse_archive_args(
        proj, archive, upstream, infiles)

    if test_dep:
        cmd_test_dep(
            upstream=upstream,
            archive=None,
            input_files=archive_files,
            distro=distro)

    if info:
        return test_info(project=proj, distro=distro)

    tests = proj.get_tests_for_distro(distro)

    if show_control:
        if not tests.control_path.exists():
            log.error('tests control file not found: %s', tests.control_path)
            return False
        if tests.extra_control:
            msg = 'extra tests control template: %s'
        else:
            msg = 'inline tests control file: %s'
        log.info(msg, tests.control_path)
        print(tests.control_text)
        return bool(tests.control_text)

    if list_tests:
        tests_ = tests.filter_tests(test_filter)
        for t in tests_:
            if t.name:
                tests_path = t.tests_dir or proj.path.tests
                cmd = str(tests_path / t.name)
            elif t.test_command:
                cmd = t.test_command
            print(cmd)
        return tests_

    log.bold("running packaging tests")
    log.info("target distro: %s", distro)

    return tests.run(test_filter=test_filter)


def test_info(project=None, distro=None):
    """
    show packaging tests info
    """
    proj = project or Project()
    distro = adistro.distro_arg(distro, proj)

    msg = "tests path:         {t.bold}{fn}{t.normal}"
    if proj.path.tests.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.error}doesn't exist{t.normal})"
    print(msg.format(fn=proj.path.tests, t=T))
    msg = "tests extras path:  {t.bold}{fn}{t.normal}"
    if proj.path.tests_extras.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " (doesn't exist)"
    print(msg.format(fn=proj.path.tests_extras, t=T))

    msg = "tests extras:"
    if proj.tests_extras:
        msg_lines = []
        for extra in proj.tests_extras:
            msg_lines.append(
                "    {t.bold}%s{t.normal}: %s: %s"
                % (extra.name, extra.selection_str(),
                   extra.distro_rules))
        msg = "\n".join([msg] + msg_lines)
    else:
        msg += "       {t.bold}N/A{t.normal}"
    print(msg.format(dir=proj.path.templates, t=T))

    print()

    # TODO: pass tvars to test control template
    tests = proj.get_tests_for_distro(distro)
    msg = "testing distro:     {t.cyan}{d}{t.normal}"
    print(msg.format(d=distro, t=T))
    msg = "tests control:      {t.bold}{p}{t.normal}"
    if tests.control_path.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.error}doesn't exist{t.normal})"
    print(msg.format(p=tests.control_path, t=T))
    msg = "tests extra:        {t.bold}{p}{t.normal}"
    print(msg.format(p=tests.extra_path or 'N/A', t=T))

    print()

    print("tests:")
    if tests.tests:
        for t in tests.tests:
            print("    {t.bold}{test}{t.normal}".format(test=t, t=T))
            if t.tests_dir:
                print("        Tests-Directory: %s" % t.tests_dir)
            if t.deps:
                print("        Depends: %s" % ", ".join(t.deps))
            if t.restrictions:
                print("        Restrictions: %s" % " ".join(t.restrictions))
    else:
        msg = "    {t.error}no tests found{t.error}"
        print(msg.format(t=T))

    return tests.tests


APKG_CLI_COMMANDS = [cli_test]
