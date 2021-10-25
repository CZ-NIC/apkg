# apkg compat

## apkg compat level

In order to allow [config file format](config.md) and functionality changes
without breaking compatibility, it's **strongly recommended** to include current
apkg compat level in the config file.

That way, `apkg` will be able work with old and new `distro/` files without
disruption in the future.


**current apkg compat level: {{ compat_level }}**

```toml
[apkg]
compat = {{ compat_level }}
```


## ensuring compatibility

!!! Important
    During `apkg` beta, backward compatibility with older versions/compat levels is provided on **best effort** basis.

    Starting from 1.0, backward compatibility is going to be **guaranteed**.


Starting with `0.3.0`, `apkg status` displays project compat level:

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

project compat level:       1
current apkg compat level:  2
latest apkg compat level:   2

current apkg version:  0.3.0
latest apkg version:   0.3.0

⚠ project compat level 1 is older than current 2

Please consider bumping

    [apkg]
    compat = 2

in project config: distro/config/apkg.toml

Inspect following upgrade notes:

# COMPAT LEVEL 2

Introduced in apkg-0.3.0

Forward compatible update for most users.

...
```

## compat level upgrade notes

You can use `compat` command's `-n`/`--notes` argument to show notes for
upgrading from the specified compat level to current:

{{ 'apkg compat --notes 1' | run }}


## compat level news

Please inspect `apkg` [news](news.md) for respective `apkg` release:

* compat level **2**: [0.3.0](news.md#apkg-030)
