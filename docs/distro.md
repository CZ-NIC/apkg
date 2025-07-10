# apkg distro

**distro** refers to an operating system distribution.

`apkg` provides simple `apkg.adistro.Distro` class to parse distro
strings such as

* `Debian`
* `Ubuntu 21.04`
* `fedora-33`

into distro **id** and optional **version** (if present) and provide consistent
selection, matching, and formatting features.


## target distro

`apkg` is a cross-distro tool but most of its commands operate on a
specific **target distro** - the distro it's building packages for.

See [apkg distro support](platforms.md#distro-support).

By default, current distro is auto-detected using python [distro] module and
used as a target distro. Check out tail of `apkg status`:

```
$> apkg status
...
current distro: arch / Arch Linux
    package style: arch
    package template: distro/pkg/arch
```

You can override target distro using `-d`/`--distro` CLI argument:

```
$> apkg status --distro debian-10
...
target distro: debian 10
    package style: deb
    package template: distro/pkg/deb
```

```
$> apkg srcpkg --distro "Ubuntu 21.04"
$> apkg build -d fedora
```


## distro rules

`apkg.adistro` module contains `DistroRule` class to represent rules against
distro id and version such as:

* `debian`: any Debian version
* `debian == 11`: Debian 11
* `ubuntu >= 21.04`: Ubuntu 21.04 or greater
* `fedora != 33`: Fedora other than 33

`apkg` is reusing python `packaging`'s [Version
Specifiers](https://packaging.pypa.io/en/latest/specifiers.html) to perform the
check.

Distro rules are used during [template selection] and also to define
[distro alias templates](templates.md#distro-alias-template) in config.

[custom templates]: custom-template

## distro aliases

**Distro alias** is a named [distro rule](#distro-rules) specified in
[apkg config](config.md#distroaliases) such as:

```toml
[[distro.aliases]]
name = "el-8"
distro = ["rocky == 8", "centos == 8", "rhel == 8"]
```

Distro aliases are available during
[template selection](templates.md#distro-alias-template) and
[rendering](templates.md#template-syntax) as a means to conveniently refer to a
set of distros without duplicating complex rules across files.


## distro in templates

`distro` template variable available during templating contains
`apkg.adistro.Distro` instance representing [target distro](#target-distro).

You can use `distro` to get distro `id` and `version` in various formats:

{% raw %}
* `{{ distro }}`: debian 10
* `{{ distro.id }}`: debian
* `{{ distro.version }}`: 10
* `{{ distro.idver }}`: debian-10
* `{{ distro.tiny }}`: deb10
{% endraw %}

It's possible to query [target distro](#target-distro) using [distro
rules](#distro-rules) from templates using `distro.match()` function. This
allows control over templating for arbitrary distro combinations:

{% raw %}
```jinja
{%- if distro.match('debian >= 11', 'ubuntu >= 21.04') %}
  * modern {{ distro.id }}
{%- else %}
  * old distro
{%- endif %}
```
{% endraw %}

Full example from {{ 'examples/templates/distro/pkg/deb/changelog' | file_link }}:

```jinja
{{ 'examples/templates/distro/pkg/deb/changelog' | file_raw }}
```


[template selection]: templates.md#template-selection
[distro]: https://github.com/python-distro/distro
