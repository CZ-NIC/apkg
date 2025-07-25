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

```toml
[project]
name = "banana"
```

This is available to templates through {% raw %}`{{ project.name }}`{% endraw %}.

### project.make_archive_script

In order to create packages from your project source,
[apkg make-archive](commands.md#make-archive) requires a script which creates
archive from current project state.

Include such script in your project and specify it using `project.make_archive_script`:

```toml
[project]
make_archive_script = "scripts/make-archive.sh"
```

When the script finishes successfully, it MUST exit with return code 0 and
print valid YAML to its stdout.

The script MUST output `archive` path:

```
archive: pkg/archives/dev/banana-v1.2.3.tar.gz
```

The script MAY output `version`:

```
version: '1.2.3'
```

When omitted, `version` is guessed from `archive` file name.

The script MAY output additional files as `components`:

```
components:
  extra: pkg/archives/dev/extra-v0.5.tar.gz
  files: pkg/archives/dev/files.tar.gz
```

The script SHOULD create archives with **unique version strings** for individual
VCS commits if using VCS. This isn't strictly required by `apkg`, but it will
save you a lot of conflicts and needless work later on.

It's strongly recommended to **reuse** the same script in the upstream archive
creation during official release so that this **code gets properly tested** on
regular basis - it's used on most `apkg` operations.

`apkg make-archive` copies the resulting `archive` (and `components` if any) to
`pkg/archives/dev` output directory. You can save some disk space and I/O by
creating the `archive` (and `components` if any) directly in `pkg/archives/dev` in your `make_archive_script`.

Most projects which use `apkg` have the script in `scripts/` directory for
historic reasons, but feel free to put it into `distro/scripts/` or anywhere
else you want.

{{ added_in_version('0.7.0', compat=6, action="Changed", extra="to YAML output") }}

For compat level 5 and older, `make_archive_script` is expected to return
archive file name as last line of its stdout:

```
pkg/archives/dev/banana-v1.2.3.tar.gz
```

`make_archive_script` **examples** in the wild:

- `apkg`: {{ 'scripts/make-archive.sh' | file_link  }}
- Knot Resolver: [scripts/make-archive.sh](https://gitlab.nic.cz/knot/knot-resolver/-/blob/master/scripts/make-archive.sh)
- Knot DNS: [scripts/make-dev-archive.sh](https://gitlab.nic.cz/knot/knot-dns/-/blob/master/scripts/make-dev-archive.sh)


## [upstream]

Config section for project upstream settings.

### upstream.archive_url

To easily download upstream archives using `apkg` you can specify
`upstream.archive_url` with [templating](templates.md) available including
special `version` variable:

{% raw %}
```toml
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
prints current upstream version to `stdout` as YAML and use it
with `upstream.version_script` option:

```toml
[upstream]
version_script = "scripts/upstream-version.py"
```

Expected script standard output in YAML:

```yaml
version: 1.2.3
```

This option overrides default auto-detection mechanism.

script example: {{ 'scripts/upstream-version.py' | file_link  }}

{{ added_in_version('0.7.0', compat=6, action="Changed", extra='to YAML output') }}

For compat level 5 and older, `upstream.version_script` is expected to return
version as last line of its stdout:

```
1.2.3
```

## [apkg]

Config section for `apkg` settings.

### apkg.compat

In order to allow config file format changes without breaking compatibility,
it's **strongly recommended** to include current apkg [compat level](compat.md)
in the config file.

That way, `apkg` will be able work with old and new formats without disruption in the future.

**current apkg compat level: {{ compat_level }}**

```toml
[apkg]
compat = {{ compat_level }}
```


## [distro]

Config section for [distro](distro.md) settings.

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


## [template]

Config section for [package template](templates.md) settings.


### template.ignore_files

A list of unix-style [file name patterns] to select files which should be
**ignored**/**skipped** during template render.

When not specified, following defaults are used:

```toml
[template]
ignore_files = {{ pkgtemplate.DEFAULT_IGNORE_FILES }}
```

To render all files instead of using defaults, simply set to an empty list:

```toml
[template]
ignore_files = []
```

### template.plain_copy_files

A list of unix-style [file name patterns] to select files which should be
copied over without templating during template render.

This option is overriden by [template.ignore_files](#templateignore_files) -
when a file matches both `ignore_files` and `plain_copy_files`, it will be
ignored.

When not specified, following defaults are used:

```toml
[template]
plain_copy_files = {{ pkgtemplate.DEFAULT_PLAIN_COPY_FILES }}
```

To template all files instead of using defaults, simply set to an empty list:

```toml
[template]
plain_copy_files = []
```

### template.variables

A list of [custom template variables sources](templatevars.md#custom-template-variables).

Example:

```toml
[[template.variables]]
python_module = "apkg.templatevars.deb_series"

[[template.variables]]
local_module = "distro/vars/custom_vars.py"
```

See [custom template variables](templatevars.md#custom-template-variables) for more info.


## [cache]

Config section for [cache](cache.md) control.

### cache.source

Set to `true` or `false` to enable or disable cache for operations
on project source files such as [make-archive](commands.md#make-archive)
and [srcpkg](commands.md#srcpkg) commands.

Project MUST be maintained in VCS (`git`) in order to enable `cache.source`.

When `cache.source = true` but VCS isn't available,
`apkg` will compain with a warning and disable it.

Read more in [source cache](cache.md#source-cache) docs.

`cache.source` is enabled by default if VCS is available:

```toml
[cache]
source = true
```

### cache.local

Set to `true` or `false` to enable or disable cache for operations
on local files such as [srcpkg](commands.md#srcpkg)
and [build](commands.md#build) commands.

`cache.local` is enabled by default:

```toml
[cache]
local = true
```

### cache.remote

Set to `true` or `false` to enable or disable cache for operations
on remote files such as [get-archive](commands.md#get-archive) command.

`cache.remote` is enabled by default:

```toml
[cache]
remote = true
```


[file name patterns]: https://docs.python.org/3/library/fnmatch.html
