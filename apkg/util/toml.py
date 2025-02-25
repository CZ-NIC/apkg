"""
wrapper to select and provide access to available TOML libraries
"""
from apkg import ex


LOAD_LIB = None
DUMP_LIB = None

LOAD_MODE = 'rb'


# get load() and loads()
try:
    from tomllib import load, loads
    LOAD_LIB = 'tomllib'
except ModuleNotFoundError:
    pass

if not LOAD_LIB:
    try:
        from tomli import load, loads
        LOAD_LIB = 'tomli'
    except ModuleNotFoundError:
        pass

if not LOAD_LIB:
    try:
        from toml import load, loads
        LOAD_LIB = 'toml'
        LOAD_MODE = 'r'
    except ModuleNotFoundError:
        pass

if not LOAD_LIB:
    try:
        from tomlkit import load, loads
        LOAD_LIB = 'tomlkit'
    except ModuleNotFoundError:
        pass


# get dump() and dumps()
try:
    from tomli_w import dump, dumps
    DUMP_LIB = 'tomli_w'
except ModuleNotFoundError:
    pass

if not DUMP_LIB:
    try:
        from tomlkit import dump, dumps
        DUMP_LIB = 'tomlkit'
    except ModuleNotFoundError:
        pass

if not DUMP_LIB:
    try:
        from toml import dump, dumps
        DUMP_LIB = 'toml'
    except ModuleNotFoundError:
        pass


def missing_toml_load_module(*args, **kwargs):
    msg=("Requested operation requires TOML load module but none was found.\n\n"
    "Please install one of following Python modules:\n\n"
    "- tomli\n- toml\n- tomlkit")
    raise ex.MissingRequiredModule(msg=msg)


def missing_toml_dump_module(*args, **kwargs):
    msg=("Requested operation requires TOML dump module but none was found.\n\n"
    "Please install one of following Python modules:\n\n"
    "- tomli_w\n- tomlkit\n- toml")
    raise ex.MissingRequiredModule(msg=msg)


# only fail when required functions are called
if not LOAD_LIB:
    load = missing_toml_load_module
    loads = missing_toml_load_module

if not DUMP_LIB:
    dump = missing_toml_dump_module
    dumps = missing_toml_dump_module


def loadp(path):
    """
    Load data from path to TOML file
    """
    with open(path, LOAD_MODE) as f:
        return load(f)
