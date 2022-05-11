"""
apkg logging module

introduces custom log levels and associated formatting using standard python
logging module

different formatting for individual log levels including optional color support

logs to stderr by default and uses colors if blessing are available and
terminal supports it, use set_color() to control

to get this nice colorful logging to terminal stderr anywhere in python:

```
from apkg.log import getLogger

log.getLogger(__name__)

log.info("log message")
log.success("great %s", "success")
```
"""
import logging
# import getLogger for convenience so that one can use
#
#   from apkg.log import getLogger
#
#   log = getLogger(__name__)
#
# to init apkg logging without the need to import logging module
# while making sure logging.setLoggerClass(ApkgLogger) was called
# (see below in this module) so that extra log level functions
# are available
from logging import getLogger  # noqa

import sys
from apkg import terminal


# add custom log levels and handle formatting
# including color based on log level
ERROR = logging.ERROR
WARN = logging.WARN
INFO = logging.INFO
VERBOSE = int((logging.INFO + logging.DEBUG) / 2)
DEBUG = logging.DEBUG
SUCCESS = WARN + 1
SUDO = WARN - 1
BOLD = INFO + 2
COMMAND = INFO + 1
VERBOSE_COMMAND = VERBOSE + 1


LOG_LEVEL_FORMATS_META = {
    ERROR: ('E', 'error'),
    SUCCESS: ('✓', 'success'),
    WARN: ('W', 'warn'),
    SUDO: ('#', 'sudo'),
    BOLD: ('I', 'bold'),
    INFO: ('I', None),
    VERBOSE: ('V', None),
    DEBUG: ('D', None),
    COMMAND: ('$', 'command'),
    VERBOSE_COMMAND: ('$', 'command'),
}


# current global log level - DON'T IMPORT/USE THIS DIRECTLY
# get LOG_LEVEL using get_log_level()
# set LOG_LEVEL using set_log_level()
LOG_LEVEL = INFO


def get_log_level():
    """
    get global log level (int)
    """
    return LOG_LEVEL


class ApkgLogger(logging.Logger):
    """
    standard logger with extra functions for custom log levels
    """
    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)

    def sudo(self, msg, *args, **kwargs):
        if self.isEnabledFor(SUDO):
            self._log(SUDO, msg, args, **kwargs)

    def bold(self, msg, *args, **kwargs):
        if self.isEnabledFor(BOLD):
            self._log(BOLD, msg, args, **kwargs)

    def verbose(self, msg, *args, **kwargs):
        if self.isEnabledFor(VERBOSE):
            self._log(VERBOSE, msg, args, **kwargs)

    def command(self, msg, *args, **kwargs):
        if self.isEnabledFor(COMMAND):
            self._log(COMMAND, msg, args, **kwargs)

    def verbose_command(self, msg, *args, **kwargs):
        if self.isEnabledFor(VERBOSE_COMMAND):
            self._log(VERBOSE_COMMAND, msg, args, **kwargs)


class LogTerminal(terminal.Terminal):
    """
    helper for handling colors when logging to terminal
    """
    @property
    def warn(self):
        return self.yellow

    @property
    def important(self):
        return self.yellow_bold

    @property
    def error(self):
        return self.red

    @property
    def success(self):
        return self.green

    @property
    def command(self):
        return self.cyan

    @property
    def sudo(self):
        return self.magenta


# global terminal instance for color printing
T = LogTerminal()


def set_colors(colors):
    """
    enable/disable colors in apkg logging terminal
    """
    global T
    if colors == 'yes':
        if not terminal.COLOR_TERMINAL:
            return False
        T = LogTerminal(force_styling=True)
        return True
    elif colors == 'no':
        if not terminal.COLOR_TERMINAL:
            return True
        T = LogTerminal(force_styling=None)
        return True
    elif colors == 'auto':
        T = LogTerminal()
        return True
    return False


def logfmt(prefix, color, levelno):
    """
    helper to generate loggin.Formatter compatible log format
    based on current log level
    """
    if color:
        color_fun = getattr(T, color)
    else:
        def color_fun(x):
            return x
    if levelno <= DEBUG:
        # prepended extra line: path, line number and function
        fmt = '%s:%s @ %s:\n%s' % (
            T.magenta('%(pathname)s'),
            T.yellow('%(lineno)s'),
            T.command('%(funcName)s()'),
            color_fun('%s %%(message)s' % prefix))
    elif levelno <= VERBOSE:
        # insert module and function name
        fmt = '%s %s.%s: %s' % (
            color_fun(prefix),
            T.magenta('%(module)s'),
            T.command('%(funcName)s()'),
            color_fun('%(message)s'))
    else:
        fmt = '%s %%(message)s' % prefix
        fmt = color_fun(fmt)
    return fmt


def render_log_level_formats(levelno):
    fmts = {}
    for level, entry in LOG_LEVEL_FORMATS_META.items():
        prefix, color = entry
        fmts[level] = logfmt(prefix, color, levelno)
    return fmts


# initialize global log formats
LOG_LEVEL_FORMATS = render_log_level_formats(LOG_LEVEL)


class ApkgLogFormatter(logging.Formatter):
    """
    default apkg log formatter with support for custom formats
    per log level including custom colors
    """
    def format(self, record):
        # change format depending on log level
        fmt = LOG_LEVEL_FORMATS.get(record.levelno, "? %(message)s")
        # this hacky but mostly reliable
        # pylint: disable=protected-access
        self._style._fmt = fmt
        # use default formatter with custom format
        return super().format(record)


# logging setup
logging.setLoggerClass(ApkgLogger)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(ApkgLogFormatter())
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)


def set_log_level(levelno):
    """
    set global log level and regenerate log formats accordingly
    """
    global LOG_LEVEL
    global LOG_LEVEL_FORMATS

    LOG_LEVEL = levelno
    logging.root.setLevel(LOG_LEVEL)
    LOG_LEVEL_FORMATS = render_log_level_formats(LOG_LEVEL)
