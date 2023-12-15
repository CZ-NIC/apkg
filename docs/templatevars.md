# apkg template variables

`apkg` provides [default template variables](#default-template-variables) which
are always available from [packaging templates](templates.md) as well as a
flexible mechanism to define [custom template variables](#custom-template-variables).

To view all template variables:

{{ 'apkg info template-variables' | run }}


## default template variables

Following template variables are always available:

* `name`: project name
* `version`: package version
* `release`: package release
* `distro`: target distro (see [distro in templates](distro.md#distro-in-templates))

Some [pkgstyles](pkgstyles.md) also define:

* `now`: current date and time in changelog format (provided only by pkgstyles
  with changelog dates such as `deb` and `rpm`)


## custom template variables

Custom template variables can be defined using [custom python
modules](#template-variables-module) and then used in [templates](templates.md)
using [template.variables](config.md#templatevariables) config option, for example:

```toml
[[template.variables]]
python_module = "apkg.templatevars.debseries"

[[template.variables]]
local_module = "distro/vars/custom_vars.py"
```

See `apkg status` output to check defined variables sources and their status:

```
$> apkg status

template variables sources:
    python_module: apkg.templatevars.debseries (exists)
    local_module: distro/vars/custom_vars.py (exists)
```

You can check which variables were defined by each custom source:

{{ 'apkg info template-variables --custom' | run }}

Or for another distro:

{{ 'apkg info template-variables -c -d ubuntu-22.04' | run }}

!!! info
    Added in `apkg` [0.5.0](news.md#apkg-050),
    [compat](compat.md) level [4](news.md#compat-level-4-news)


### template variables module

Custom variables can be passed to `apkg` using a python module which defines
`get_variables` function like this:

```python
def get_variables(old_vars : dict) -> dict:
    return dict(...)
```

Existing template variables are passed to `get_variables` function as a `dict`
argument and the function is expected to return a `dict` of custom variables.

See {{ 'apkg/templatevars/debseries.py' | file_link }} for an example
implementation.


### local variables module

Project-local python module files can be used with `local_module`
[template.variables](config.md#templatevariables) config:

```toml
[[template.variables]]
local_module = "distro/vars/custom_vars.py"
```

!!! TIP
    A recommended directory to place your custom variables modules is

    ```
    distro/vars
    ```

    but you can put them anywhere in the project repo.

!!! NOTE
    Loading the local module files can produce `__pycache__` directory.

    If you use them, don't forget to add `__pycache__` to your `.gititnogre`.


### python variables module

Global Python modules can be used with `python_module`
[template.variables](config.md#templatevariables) config:

```toml
[[template.variables]]
python_module = "apkg.templatevars.debseries"
```


## apkg built-in template variables modules

`apkg.templatevars` currently contains a single template variables module:


### apkg.templatevars.debseries

Extract distro series (`deb_series`) and codename (`deb_codename`) from

```
/usr/share/distro-info/$DISTRO.csv
```

file provided by `distro-info-data` package.

When no info is found for distro, return `unstable` / `Sid`.

Provides custom template variables:

* `deb_series` : `str`
    * examples: `bookworm`, `noble`, `unstable`
* `deb_codename` : `str`
    * examples: `Bookworm`, `Noble Numbat`, `Sid`

Enable by adding [template.variables](config.md#templatevariables)
entry to config:

```toml
[[template.variables]]
python_module = "apkg.templatevars.debseries"
```

Example usage in `debian/chanelog`:

{% raw %}
```jinja
some-package ({{ version }}-{{ release }}~{{ deb_series }}) {{ deb_series }}; urgency=medium

* upstream package version {{ version }} for {{ distro }} {{ deb_codename }}

-- Jakub Ružička <jakub.ruzicka@nic.cz>  {{ now }}
```
{% endraw %}

!!! info
    Added in `apkg` [0.5.0](news.md#apkg-050),
    [compat](compat.md) level [4](news.md#compat-level-4-news)
