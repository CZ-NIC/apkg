# apkg commands

To get a summary of available `apkg` commands, simply run it without parameters:

{{ 'apkg' | run }}

Use `--help`/`-h` after a command to get help for that particular command instead:

```
$> apkg command --help
```

## status

{{ 'status' | cmd_help }}

Example:

```
$> apkg status

project name:            apkg
project base path:       /home/u/src/apkg
project VCS:             git
project config:          distro/config/apkg.toml (exists)
package templates path:  distro/pkg (exists)
package templates:
    arch: arch pkgstyle default: arch
    deb: deb pkgstyle default: ubuntu | debian | linuxmint | raspbian
    nix: nix pkgstyle default: nix | nixos
    rpm: rpm pkgstyle default: fedora | centos | rocky | rhel | opensuse | oracle | pidora | scientific

current distro: arch / Arch Linux
    package style: arch
    package template: distro/pkg/arch
```


## system-setup

{{ 'system-setup' | cmd_help }}


## make-archive

{{ 'make-archive' | cmd_help }}

`make-archive` requires
[project.make_archive_script](config.md#projectmake_archive_script)
config option to be set.

This command will only succeed when the script finishes successfully (with
exit code 0) and the resulting archive it created and printed to stdout
followed by one line for each additional file (like signature).

Resulting archive is copied to `pkg/archives/dev/` or to `--result-dir`.

Resulting archive is cached if [cache.source](config.md#cachesource)
is enabled. See [source cache](cache.md#source-cache) for requirements.


## get-archive

{{ 'get-archive' | cmd_help }}

`get-archive` requires
[upstream.archive_url](config.md#upstreamarchive_url)
config option to be set with additional options available in
[upstream config section](config.md#upstream).

This command will only succeed when it managed to download specified archive.

Archive is downloaded into `pkg/archives/upstream/` or to `--result-dir`.

If automatic latest upstream version detection doesn't work,
you can always supply version manually with `-v`/`--version` option,
i.e. `apkg get-archive -v 1.2.3`

Resulting archive is cached if [cache.remote](config.md#cacheremote)
is enabled.


## srcpkg

{{ 'srcpkg' | cmd_help }}

Resulting source package is cached if both [cache.local](config.md#cachelocal) and
[cache.source](config.md#cachesources) are enabled, unless using `--upstream`
which only requires [cache.local](config.md#cachelocal).
See [source cache](cache.md#source-cache) for more info.

## build

{{ 'build' | cmd_help }}

Resulting packages are cached if [cache.local](config.md#cachelocal) is enabled.

## build-dep

{{ 'build-dep' | cmd_help }}


## install

{{ 'install' | cmd_help }}


## clean

{{ 'clean' | cmd_help }}


## test

{{ 'test' | cmd_help }}

See [test command examples](test.md#test-command-examples)


## test-dep

{{ 'test-dep' | cmd_help }}
