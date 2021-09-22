# apkg packaging styles

In order to support different packaging formats, tools, and systems, `apkg`
introduces the concept of **packaging style**. Each packaging style in
`apkg.pkgstyles` such as `deb`, `rpm`, or `arch` contains common functions to
perform packaging on a corresponding packaging platform.

`apkg.pkgstyle` module provides discovery of individual packaging styles which
are in turn used to handle packaging on [target distro](distro.md#target-distro)
by `apkg` commands such as `apkg srcpkg` and `apkg build`.

This means that all platform specific code is contained in separate files
(`arch.py`, `deb.py`, `rpm.py`) which are maintained independently. Breakage in
`apkg.pkgstyles.rpm` will only affect builds on `rpm` platforms. New packaging
styles can be added easily, external plugin support is planned.

When needed by `apkg`, packaging style is chosen automatically based on [target
distro](distro.md#target-distro) and/or files present in selected
[package template](templates.md).

Each `pkgstyle` provides `SUPPORTED_DISTROS` list of supported distro IDs as
returned by python [distro module](https://pypi.org/project/distro/).


{% for ps in pkgstyles.values() %}
## {{ ps.name }}

{{ ps.__doc__}}

**supported distros:** {% for sd in ps.SUPPORTED_DISTROS %}`{{ sd }}`{% if not loop.last %} , {% endif %}{% endfor %}

**file:** {{ ps.__file__ | file_link }}

{% endfor %}
