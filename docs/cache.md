# apkg cache

`apkg` caches most of its command outputs as package
building can take considerable amounts of resources.

Output files in [output directory](intro.md#output) are cached when viable in a single `apkg` cache file `pkg/.cache.json`.

To view cache conetnts:

```
apkg info cache
```

To remove cache file only without affecting output files:

```
apkg clean --cache
```

All caching can be disabled per command using `--no-cache` argument:

```
apkg srcpkg --no-cache
```

See [cache config](config.md#cache) for fine control over different cache targets.


## source cache

In order to get meaningful caching for [make-archive](commands.md#make-archive)
and [srcpkg](commands.md#srcpkg) commands which operate on project sources:

* All project sources MUST be properly maintained in VCS (`git`).

* [cache.source](config.md#cachesource) MUST be enabled. It's enabled by default
  if VCS is present.

* [project.make_archive_script](config.md#projectmake_archive_script) MUST be set.
