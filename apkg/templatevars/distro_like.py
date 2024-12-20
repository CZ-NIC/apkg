"""
Custom template variable module for apkg adding an enhanced distro variable.

Provides custom template variable `distro_like` that behaves exactly like
`distro`, except that a `distro_like.match()` also matches against the ID_LIKE
information from the distro (e.g. CentOS has rhel in there, ...) respecting the
version as well. As such, version matching should be done only when the derived
distro's version scheme is compatible (e.g. Ubuntu doesn't match Debian's).

This behaviour does not trigger in all cases, if `-d <distro maybe-version>` is
passed to apkg and the distro specified that way is different from the one
inferred from the current host, this new variable will *not* be exposed. This
gives the packager a chance to detect and handle this case however they see
fit, e.g. by setting `distro_like` themselves while preventing running a build
with an untested configuration accidentally.

Enable by adding [[template.variables]] entry to distro/config/apkg.toml:

    [[template.variables]]
    python_module = "apkg.templatevars.distro_like"

Example usage in rpm spec:

{% if distro_like.match('rhel > 9') %}
{# this also matches on Alma 9, CentOS 10, Rocky 28, ... #}
{% endif %}
"""  # noqa

import distro

from apkg import adistro


# called by apkg to get custom variables
def get_variables(env):
    distro_var = env['distro']
    # poor man's .copy()
    distro_like = adistro.Distro(distro_var.orig, distro.aliases)

    if distro.id.lower() == distro_var.id.lower():
        like = set(distro_var.names) + set(distro.like().split())
        distro_like.names = list(like)
        return {'distro_like': distro_like}

    # Otherwise building for a foreign distro, expose nothing
    return {}
