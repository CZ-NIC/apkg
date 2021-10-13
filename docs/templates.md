# apkg package templates

In order to maintain packages for families of distros using same
[packaging style](pkgstyles.md) with minimal redundancy, `apkg` supports
templating through [jinja] templating engine.

Individual directories in templates directory `distro/pkg/` are considered
**package templates** each using a particular [packaging style](pkgstyles.md)
which is determined automatically by `apkg` based on files present in a
template.

!!! TIP
    See minimal example of `apkg` templating features:

    * {{ 'examples/templates' | file_link }}

    You can also refer to `apkg` templates:

    * {{ 'distro/pkg' | file_link }}


## template syntax

`apkg` uses [jinja] the great python templating engine on all files in a package template by default.

There's currently a hardcoded mechanism to copy problematinc files (i.e. patches) over without
templating which should be exposed through config or a `.gitignore`-like file in the future.

You can use all [jinja] templating features with following variables provided by `apkg`:

* `name`: project name
* `version`: package version
* `release`: package release
* `distro`: target distro (see [distro in templates])
* `now`: current date and time in changelog format (provided only by pkgstyles
  with changelog dates such as `deb` and `rpm`)

[include] tag is also supported and can be used to include
files relative to project root.

Example Debian `changelog`:

```jinja
{{ 'examples/templates/distro/pkg/deb/changelog' | file_raw }}
```

See [distro in templates] to learn howto use the magical `distro` object in
templates.


## template selection

`apkg` selects package template (from `distro/pkg/`) to use based on [target
distro].

To cover simple use cases without configuration but still allow full control
when needed, `apkg` provides 3 types of template selection mechanisms (described
below) which can be combined as needed.

Use `apkg status` to list available package templates ordered by priority.

You can also supply `apkg status` with `--distro` argument to check which
template gets selected on a particular distro:

```
$> apkg status --distro debian-10
...
package templates:
    arch: arch pkgstyle default: arch
    deb: deb pkgstyle default: ubuntu | debian | linuxmint | raspbian

target distro: debian 10
    package style: deb
    package template: distro/pkg/deb
```


### pkgstyle default template

The simplest and most general type of template that is used for any
distro supported by selected [packaging style](pkgstyles.md).

Simply name the template directory in `distro/pkg/` the same as the desired
[packaging style](pkgstyles.md) such as `deb`, `rpm`, or `arch` and it will be
used as a default for all distros supported by that style.

It's recommended to start with pkgstyle default templates and cover special
cases using other template types as needed.

Many simple projects will do just fine with pkgstyle default templates only.


### distro-specific template

Templates in `distro/pkg/` which aren't named as an existing [packaging
style](pkgstyles.md) are considered to be **distro-specific**. They are selected by
`apkg` based on their name.

In simplest case, distro-specific template is only selected when target distro
matches its name:

* `debian`: any Debian version (but not clones)
* `ubuntu`: any Ubuntu version
* `fedora`: any Fedora version

Additionally, specific distro version can be requested using `-` (dash) separator:

* `debian-10`: Debian 10
* `ubuntu-20.04`: Ubuntu 20.04
* `fedora-36`: Fedora 36

Only numeric versions are supported, codenames such as `buster` or `Focal Fosa`
won't work.


### distro alias template

Distro alias templates provide full control over their selection based on
[distro aliases](distro.md#distro-aliases)
defined in [config](config.md#distroaliases).

When a package template name matches a defined [distro
alias](distro.md#distro-aliases), its distro rules are used to select the
template.

For example to use `deb-old` distro alias defined as follows:

```toml
[[distro.aliases]]
name = "deb-old"
distro = ["debian < 9", "ubuntu < 20.04"]
```

simply create `distro/pkg/deb-old` template and `apkg` will select it based on
supplied distro rule - on Debian versions older than 9 and on Ubuntu versions
older than 20.04.


## import existing packaging

To import existing packaging sources as `apkg` templates simply copy them into a
new template dir in `distro/pkg/` (see [templates selection](templates.md#template-selection))
and replace all occurrences of:

{% raw %}
* package **version** string with `{{ version }}`
* package **release** string with `{{ release }}` (optional)
* changelog **date** with `{{ now }}` (optional for pkgstyles with changelogs like `deb` and `rpm`)
{% endraw %}


### import debian-based packaging

{% raw %}
``` bash
cp -r ~/debian/foo/debian distro/pkg/deb
edit distro/pkg/deb/changelog
# replace VERSION-RELEASE string with {{ version }}-{{ release }}
# replace date with {{ now }}
```
{% endraw %}

Examples:

* apkg `deb` template: {{ 'distro/pkg/deb' | file_link }}
* templates example `deb` template: {{ 'examples/templates/distro/pkg/deb' | file_link }}


### import rpm packaging

{% raw %}
``` bash
cp -r ~/fedora/foo distro/pkg/rpm
edit distro/pkg/rpm/foo.spec
# replace Version string to {{ version }}
# replace Release string to {{ release }} (leave %{?dist} at the end if present)
# replace changelog date with {{ now }}
```
{% endraw %}

Examples:

* apkg `rpm` template: {{ 'distro/pkg/rpm' | file_link }}
* templates example `rpm` template: {{ 'examples/templates/distro/pkg/rpm' | file_link }}


[jinja]: https://jinja.palletsprojects.com/en/3.0.x/templates/
[include]: https://jinja.palletsprojects.com/en/3.0.x/templates/#include
[distro in templates]: distro.md#distro-in-templates
[target distro]: distro.md#target-distro
