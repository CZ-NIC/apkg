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

!!! Important
    During `apkg` beta, backward compatibility with older versions/compat levels is provided on **best effort** basis.

    Starting from 1.0, backward compatibility will be **ensured**.


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

project compat level:       3
current apkg compat level:  4
latest apkg compat level:   4

current apkg version:  0.5.1
latest apkg version:   0.5.1

⚠ project compat level 3 is older than current 4

Please consider bumping

    [apkg]
    compat = 4

in project config: distro/config/apkg.toml

Inspect following upgrade notes:

# COMPAT LEVEL 4

Introduced in apkg-0.5.0

Forward compatible update, no action required.
```

## compat level upgrade notes

You can use `compat` command's `-n`/`--notes` argument to show notes for
upgrading from the specified compat level to current:

{{ 'apkg compat --notes 1' | run }}


## compat level news

Please inspect apkg [news](news.md) for respective release:

* compat level **4**: [0.5.0](news.md#apkg-050)
* compat level **3**: [0.4.0](news.md#apkg-040)
* compat level **2**: [0.3.0](news.md#apkg-030)
