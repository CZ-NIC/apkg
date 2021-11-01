# apkg packaging guide

This guide assumes you have:

* read [apkg intro](intro.md)
* [installed apkg](install.md)


## apkg packaging workflow

``` text

                        apkg packaging workflow

 +------------------------------+    +------------------------------------+
 |                              |    |                                    |
 |     $ apkg make-archive      |    |     $ apkg get-archive [-v 1.2.3]  |
 |                              |    |                                    |
 |   in: current project state  | OR |   in: archive hosted online        |
 |                              |    |                                    |
 |  out: pkg/archives/dev/*.xz  |    |  out: pkg/archives/upstream/*.xz   |
 |                              |    |                                    |
 +---------------+--------------+    +----------------+-------------------+
                 |                                    |
                 |                                    |
                 |                                    |
                 v                                    v
      +----------+------------------------------------+-------------+
      |                                                             |
      |     $ apkg srcpkg                                           |
      |                                                             |
      |   in: distro/pkg/$TEMPLATE/  (package template)             |
      |       pkg/archives/*/*.xz    (archive)                      |
      |                                                             |
      |  out: pkg/srcpkgs/$DISTRO/$SRCPKG         (source package)  |
      |       pkg/build/srcpkgs/$DISTRO/$SRCPKG/  (build dir)       |
      |                                                             |
      +------------------------------+------------------------------+
                                     |
                                     |
                                     |
                                     v
      +------------------------------+------------------------------+
      |                                                             |
      |     $ apkg build                                            |
      |                                                             |
      |   in: pkg/srcpkgs/$DISTRO/$SRCPKG  (source package)         |
      |                                                             |
      |  out: pkg/pkgs/$DISTRO/$PKG        (package)                |
      |       pkg/build/pkgs/$DISTRO/$PKG  (build dir)              |
      |                                                             |
      +-------------------------------------------------------------+
```


## usage

To get a summary of available [commands](commands.md) simply run `apkg` without parameters.

Use `--help`/`-h` after a command to get help for that particular command instead:

``` text
$> apkg build -h
```

Detailed description of each command is available in [commands docs](commands.md).

You can control `apkg` output format and verbosity using `-L`/`--log-level` option:

* `-L debug`: print everything; include source file, line number, and function name
* `-L verbose`: print more things; include module name and function
* `-L info`: print normal amount of things - default
* `-L brief`: only print important things like success, errors, and command output
* `-L quiet`: suppress all logging output, only print command results

Please note that the option must be specified **before apkg sub-command**, i.e.:

```
apkg -L verbose build -b
```

!!! tip
    `-L verbose` and `-L debug` options can be **very helpful** when debugging, try adding one before your failing `apkg` command to gain more insight.


## system setup

In order to setup a system for packaging with apkg, run:

```
apkg system-setup
```

This will install required system packages depending on current distro
such as `rpm-build` on Fedora or `devscripts` on Debian.


## project setup

All `apkg` input files reside in top-level `distro/` directory by convention.

In order to use `apkg` in your project you need to provide it with:

* configuration in `distro/config/apkg.toml`
* package templates in individual directories of `distro/pkg/`

Let's start by entering top level project dir and creating `distro/` there:

```
cd project
mkdir distro
```

### project config - apkg.toml

Let's create `distro/config` directory and open new `apkg.toml` in your favorite editor:

``` shell
mkdir distro/config
edit distro/config/apkg.toml
```

You can use `apkg`'s {{ 'distro/config/apkg.toml' | file_link }} as a starting point.

See [apkg config docs](config.md) for a
complete list of individual `apkg.toml` options including descriptions.

This guide assumes you have following options specified in your `apkg.toml`:

* [project.name](config.md#projectname)
* [project.make_archive_script](config.md#projectmake_archive_script)
* [upstream.archive_url](config.md#upstreamarchive_url) if project has upstream archives

Confirm that `apkg status` in project directory mentions existing config file:

``` text
$> apkg status | grep 'project config'

project config:          distro/config/apkg.toml (exists)
```

Test `project.make_archive_script` option using `apkg make-archive`:

``` text
$> apkg make-archive

I creating dev archive
I running make_archive_script: scripts/make-archive.sh
I archive created: dist/apkg-0.0.2.tar.gz
I copying archive to: pkg/archives/dev/apkg-0.0.2.tar.gz
✓ made archive: pkg/archives/dev/apkg-0.0.2.tar.gz
pkg/archives/dev/apkg-0.0.2.tar.gz
```

!!! tip
    If you run into issues, consider inserting `-L verbose` or `-L debug` before
    the failing command to print more detailed information.

Great, you're now able to create archives required to create packages!


### package templates

Next we need to create individual [package templates](templates.md) to contain
all files needed to create source package using one of supported
[packaging styles](pkgstyles.md).

Each directory in `distro/pkg/` is considered a template.

{% raw %}
Version string should be replaced with `{{ version }}` macro in relevant files
and such templating is available for all files present in a template - you can
reference `{{ project.name }}` and more.
{% endraw %}

This is best demonstrated on `apkg` itself:

* `arch` template: {{ 'distro/pkg/arch' | file_link }}
* `deb` template: {{ 'distro/pkg/deb' | file_link }}
* `rpm` template: {{ 'distro/pkg/rpm' | file_link }}

{% raw %}
!!! TIP
    `apkg` doesn't provide means to create new templates automatically as that's
    handled on distro level.

    Just use standard way of creating packages on the
    target platform, put the resulting files into template dir and adjust
    `{{ version }}`.

    Use target distro's packaging docs and use similar packages
    already in distro repos as a reference.
{% endraw %}

Please consult [package template docs](templates.md) alongside target distro
packaging docs and you should eventually arrive at `apkg status` mentioning
newly created package templates:

``` text
$> apkg status

project name:            project
project base path:       /home/u/src/project
project VCS:             git
project config:          distro/config/apkg.toml (exists)
package templates path:  distro/pkg (exists)
package templates:
    arch: distro/pkg/arch
    deb: distro/pkg/deb

current distro: arch / Arch Linux
    package style: arch
    package template: distro/pkg/arch
```


## build dependencies

`apkg` is able to parse and install build requires directly from
[templates](templates.md) as well as from source packages.

To install project build deps for current distro:

```
apkg build-dep
```

Alternatively, you can only list build deps and install/process them as you see fit:

```
apkg build-dep -l
```


## build packages

`apkg build` is a primary `apkg` command used to build packages that should
cover vast majority of use cases.

Try running `apkg build` and see what it says. `apkg` should explain clearly
if something is wrong, if that's not the case please do open a
[new issue]({{ new_issue_url }}) as that's a serious usability problem.

Here is an example of successful `apkg build` run on Arch linux (with
output filtered using `--brief` option to success/error messages only):

``` text
arch$> apkg build

✓ made archive: pkg/archives/dev/apkg-0.0.2.tar.gz
✓ made source package: pkg/srcpkgs/arch/apkg-0.0.2-1/PKGBUILD
✓ built 1 packages in: pkg/pkgs/arch/apkg-0.0.2-1
pkg/pkgs/arch/apkg-0.0.2-1/apkg-0.0.2-1-any.pkg.tar.zst
```

Same command in the very same dir on Debian machine:

``` text
debian$> apkg build

✓ made archive: pkg/archives/dev/apkg-0.0.2.tar.gz
✓ made source package: pkg/srcpkgs/debian-unstable/apkg-0.0.2-1/apkg_0.0.2-1.dsc
✓ built 1 packages in: pkg/pkgs/debian-unstable/apkg_0.0.2-1
pkg/pkgs/debian-unstable/apkg_0.0.2-1/python3-apkg_0.0.2-1_all.deb
```

To minimize waiting time, `apkg` automatically caches and reuses
archives/source packages/packages produced by individual commands as long
as project is managed by VCS (`git`) and `--no-cache` wasn't supplied.

Re-running the command without changes to project source code results in
`apkg` reusing cached files from previous run:

``` text
debian$> apkg build

✓ reuse cached archive: pkg/archives/dev/apkg-0.0.2.tar.gz
✓ reuse cached source package: pkg/srcpkgs/debian-unstable/apkg-0.0.2-1/apkg_0.0.2-1.dsc
✓ reuse 1 cached packages from: pkg/pkgs/debian-unstable/apkg_0.0.2-1
pkg/pkgs/debian-unstable/apkg_0.0.2-1/python3-apkg_0.0.2-1_all.deb
```

## output directory pkg/

You've probably noticed by now that `apkg` outputs all files
into `pkg/` directory as described in [intro output section](intro.md#output).

**You can delete entire `pkg/` directory** at any time as it only contains
output that can be re-created by re-running apkg commands.

!!! TODO
    This guide deserves more content ✍🏽

!!! tip
    See [projects using apkg](users.md) 👀
