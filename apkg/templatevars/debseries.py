"""
Backward compatibility wrapper for debseries -> deb_series rename.

Please use deb_series module instead, this is going to be removed for 1.0.
"""  # noqa

from apkg.templatevars import deb_series
from apkg.log import getLogger


log = getLogger(__name__)


# called by apkg to get custom variables
def get_variables(env):
    log.warning("apkg.templatevars.debseries renamed to deb_series. "
                "Please use apkg.templatevars.deb_series instead.")
    return deb_series.get_variables(env)
