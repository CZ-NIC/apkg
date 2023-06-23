class NullCallableString(str):
    """
    This emulates blessed class for cases when blessed isn't available
    """
    def __new__(cls):
        return str.__new__(cls, '')

    def __call__(self, arg, *extra_args):
        if isinstance(arg, int):
            return ''
        return arg


class PlainTerminal:
    """
    Mock of blessed Terminal that ignores formatting
    """
    nullstr = NullCallableString()

    def __getattr__(self, attr):
        setattr(self, attr, self.nullstr)
        return self.nullstr


COLOR_TERMINAL = False
try:
    try:
        import blessed
    except Exception:
        import blessings as blessed
    # this can throw _curses.error: setupterm: could not find terminal
    # better find out now
    blessed.Terminal()
    Terminal = blessed.Terminal
    COLOR_TERMINAL = True
except Exception:
    Terminal = PlainTerminal
