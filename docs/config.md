# apkg config

`apkg` looks for config file `distro/config/apkg.toml`.

Please see {{ 'distro/config/apkg.toml' | file_link }} for up-to-date example.

This document describes apkg
[compat level](#apkgcompat) **{{ compat_level }}**
config options.


## [project]

The primary config section containing project-specific settings.

### project.name

By default, project name is guessed from project dir name but that can break
easily when the project dir is renamed so it's better to specify it explicitly
in using `project.name`

```
[project]
name = "banana"
```

This is available to templates through {% raw %}`{{ project.name }}`{% endraw %}.

### project.make_archive_script

In order to create packages from your project source, `apkg` requires a script
which creates archive from current project state.

The script MUST return the path to created archive on first line of its
`stdout`.

The script can output additional files (such as signatures) and print their
paths on individual `stdout` lines after the main archive.

Include such script in your project and then point to it using `make_archive_script`:

```
[project]
make_archive_script = "scripts/make-archive.sh"
```

script example: {{ 'scripts/make-archive.sh' | file_link  }}

## [upstream]

Config section related to project upstream settings.

### upstream.archive_url

To easily download upstream archives using `apkg` you can specify
`upstream.archive_url` with [templating](templates.md) available including
special `version` variable:

{% raw %}
```
[upstream]
archive_url = "https://banana.proj/dl/{{ project.name }}/{{ project.name }}-{{ version }}.tar.xz"
```
{% endraw %}

### upstream.signature_url

Optional signature file to download alongside upstream archive.

### upstream.version_script

If default upstream version auto-detection from HTML listing of files at
`upstream.archive_url` parent doesn't work for your project or you want full
control over the process, you can create a custom executable script which
prints current upstream version to `stdout` and tell `apkg` to use it
with `upstream.version_script` option:

```
[upstream]
version_script = "scripts/upstream-version.py"
```

This option overrides default auto-detection mechanism.

script example: {{ 'scripts/upstream-version.py' | file_link  }}


## [apkg]

Config section related to `apkg` configuration and settings.

### apkg.compat

In order to allow config file format changes without breaking compatibility,
it's **strongly recommended** to include current apkg compatibility level in the config file.

That way `apkg` will be able work with old and new config formats without disruption in the future.

**current apkg compat level: {{ compat_level }}**

```
[apkg]
compat = {{ compat_level }}
```


## [distro]

Config section related to distro configuration.

### distro.aliases

A list of custom [distro aliases](distro.md#distro-aliases).

```toml
[[distro.aliases]]
name = "deb-old"
distro = ["debian <= 9", "ubuntu < 20.04"]

[[distro.aliases]]
name = "el-8"
distro = ["rocky == 8", "centos == 8", "rhel == 8"]
```
