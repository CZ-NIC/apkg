# apkg compat

## apkg compat level

In order to allow [config file format](config.md) and functionality changes
without breaking compatibility, it's **strongly recommended** to include current
apkg compat level in the config file.

That way, apkg will be able work with old and new `distro/` files without
disruption in the future.


**current apkg compat level: {{ compat_level }}**

```toml
[apkg]
compat = {{ compat_level }}
```


## ensuring compatibility

`apkg status` displays project compat level:

```
$> apkg status

project compat level:    {{ compat_level }} (current)
```

If the project compat level doesn't match the current compat level of installed
`apkg` version (or it isn't set), `apkg` will mention this:

```
$> apkg status

project compat level:    1 (old -> run apkg compat)
```

As `apkg` suggests, its `compat` command exists to provide instructions for
setting the proper compat level in the project config including actions required
for upgrade if any:


```
$> apkg compat

project compat level:       4
current apkg compat level:  6
latest apkg compat level:   6

current apkg version:  0.7.1
latest apkg version:   0.7.1

⚠ project compat level 4 is older than current 6

Please consider bumping

    [apkg]
    compat = 6

in project config: distro/config/apkg.toml

Inspect following upgrade notes:

# COMPAT LEVEL 5

Introduced in apkg-0.6.0

Forward compatible update for most users.

## RPM macros in .spec templates are now evaluated using rpmspec if available

This might result in different build deps being detected by apkg when using
%if macros on BuildRequires. Results depend on rpmspec availability
and macros defined on the host machine (such as %fedora).

# COMPAT LEVEL 6

Introduced in apkg-0.7.0

Forward incompatible update, changes required:

## new make_archive_script YAML interface

make_archive_script stdout is now expected to be in YAML format, any messages
should go to stderr.

Edit your make_archive_script to output like this:

archive: pkg/archives/dev/banana-1.2.3.tar.gz
```

## compat level upgrade notes

You can use `compat` command's `-n`/`--notes` argument to show notes for
upgrading from the specified compat level to current:

{{ 'apkg compat --notes 1' | run }}


## compat level news

Please inspect apkg [news](news.md) for respective release:

* compat level **6**: [0.7.0](news.md#apkg-070)
* compat level **5**: [0.6.0](news.md#apkg-060)
* compat level **4**: [0.5.0](news.md#apkg-050)
* compat level **3**: [0.4.0](news.md#apkg-040)
* compat level **2**: [0.3.0](news.md#apkg-030)
