# apkg packaging guide

This guide assumes you have:

* read [apkg intro](intro.md)
* [installed apkg](install.md)


## apkg packaging workflow

### graphical diagram of apkg workflow

``` mermaid
flowchart TD
    upstream[upstream repo]
    sources[project sources]
    archive[archive / tarball]
    srcpkg[source package]
    pkg[binary packages]
    pkg-installed[installed packages]
    pkg-tests[packaging tests]
    lint[packaging linter output]
    upstream -- git clone --> sources
    sources -- apkg make-archive --> archive
    upstream -- apkg get-archive --> archive
    sources -. apkg srcpkg .-> srcpkg
    archive -- apkg srcpkg --> srcpkg
    srcpkg -- apkg build --> pkg
    pkg -- apkg install --> pkg-installed
    pkg-installed -- apkg test --> pkg-tests
    pkg -- apkg lint --> lint
    srcpkg -- apkg lint --> lint
```

### text diagram of apkg workflow

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
 +--------------+---------------+    +-----------------+------------------+
                |                                      |
                |                                      |
                |                                      |
                v                                      v
      +---------+--------------------------------------+------------+
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
      |  out: pkg/pkgs/$DISTRO/$PKG        (packages)               |
      |       pkg/build/pkgs/$DISTRO/$PKG  (build dir)              |
      |                                                             |
      +---------+--------------------------------------+------------+
                |                                      |
                |                                      |
                |                                      |
                v                                      v
 +--------------+---------------+    +-----------------+------------------+
 |                              |    |                                    |
 |     $ apkg install           |    |     $ apkg lint                    |
 |                              |    |                                    |
 |   in: pkg/pkgs/$DISTRO/$PKG  |    |   in: pkg/srcpkgs/$DISTRO/$SRCPKG  |
 |       (packages)             |    |       pkg/pkgs/$DISTRO/$PKG        |
 |                              |    |                                    |
 |  out: packages installed     |    |  out: native distro linter output  |
 |       on host system         |    |                                    |
 |                              |    +------------------------------------+
 +--------------+---------------+
                |
                |
                |
                v
      +---------+---------------------------------+
      |                                           |
      |     $ apkg test                           |
      |                                           |
      |   in: distro/tests  (packaging tests)     |
      |       packages installed on host system   |
      |                                           |
      |  out: run packaging tests on host system  |
      |                                           |
      +-------------------------------------------+
```



## usage

To get a summary of available [commands](commands.md) simply run `apkg` without parameters:

```
$> apkg
```

Use `-h`/`--help` after a command to get help for that particular command instead:

```
$> apkg build -h
```

To get an overview of `apkg`-managed project in current directory, use `apkg status`:

```
$> apkg status
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

In order to setup a system for packaging with `apkg`, run:

```
apkg system-setup
```

This will install required core packages for direct package build depending on
current distro such as `rpm-build` on Fedora or `devscripts` on Debian.

You can select which system packages to install using `system-setup` options:

```
  -c, --core         install core packages for direct package builds [default]
  -I, --isolated     install packages for isolated package builds
  -L, --lint         install packages for linting (apkg lint)
  -a, --all          install all of above (-cIL)
```

To enable isolated package builds (`apkg build --isolated`), use `--isolated`:

```
apkg system-setup --isolated
```

To install packaging linter needed for [apkg lint](commands.md#lint),
use `--lint`:

```
apkg system-setup --lint
```

Combine the options to select the packages you need.

For example, if you're setting up CI image to run standard `apkg` commands as
well as `apkg lint`, use `--core` and `--lint`:

```
apkg system-setup --core --lint
```

Or you can use `--all` to install all packages apkg needs for any of its commands:

```
apkg system-setup --all
```


## project setup

All `apkg` input files reside in top-level `distro/` directory by convention.

In order to use `apkg` in your project you need to provide it with:

* [configuration](config.md) in `distro/config/apkg.toml`
    * including [make_archive_script](config.md#projectmake_archive_script)
* [package templates](templates.md) in individual directories of `distro/pkg/`

Let's start by entering top level project dir and creating `distro/` there:

``` shell
cd project
mkdir distro
```


### make_archive_script

In order to automate anything, we need to be able to create archives directly
from project sources.

Archive creation is an important step which tends to differ from project to
project so it's recommended to isolate it into a dedicated script.

Please see [make_archive_script docs](config.md#projectmake_archive_script) and
create such script.


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
* [apkg.compat](config.md##apkgcompat)

Confirm that `apkg status` in project directory mentions existing config file:

``` text
$> apkg status

project config:          distro/config/apkg.toml (exists)
```

You can view current project config using `apkg info config`:

``` text
$> apkg info config
I project config: distro/config/apkg.toml
```
``` toml
[project]
name = "foo"
make_archive_script = "scripts/make-archive.sh"

[apkg]
compat = 6
```


### make archive

With [project.make_archive_script](config.md#projectmake_archive_script) config
set, `apkg make-archive` should be able to create archives from project sources:

``` mermaid
flowchart TD
    sources[project sources] -- apkg make-archive --> archive
```

``` text
$> apkg make-archive

I creating dev archive
I running make_archive_script: scripts/make-archive.sh
I archive created: pkg/archives/dev/foo-v0.5.1.tar.gz
✓ made archive: pkg/archives/dev/foo-v0.5.1.tar.gz
pkg/archives/dev/foo-v0.5.1.tar.gz
```

!!! tip
    If you run into issues, consider inserting `-L verbose` or `-L debug` before
    the failing command to print more detailed information.

Great, you're now able to create archives required to create source packages!


### package templates

Next we need to create individual [package templates](templates.md) to contain
all files needed to create source package using one of supported
[packaging styles](pkgstyles.md).

Each directory in `distro/pkg/` is considered a template.

{% raw %}
Version string should be replaced with `{{ version }}` macro in relevant files
and such templating is available for all files present in a template - you can
reference `{{ project.name }}` and more with the power of [Jinja](https://jinja.palletsprojects.com/).
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

project name:            foo
project base path:       /home/u/src/foo
project VCS:             git
project config:          distro/config/apkg.toml (exists)
project compat level:    4 (current)

package templates path:  distro/pkg (exists)
package templates:
    deb: deb pkgstyle default: debian | linuxmint | pop | raspbian | ubuntu
    rpm: rpm pkgstyle default: almalinux | centos | fedora | opensuse | oracle | pidora | rhel | rocky | scientific
template variables sources:
    no custom variables sources defined

current distro: debian 12 / Debian GNU/Linux 12 (bookworm)
    package style: deb
    package template: distro/pkg/deb
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

Getting correct build dependencies from packaging templates implies correct
template setup - you're ready to build source package.


## build source package

With [templates](templates.md) in place (`distro/pkg/`) and `apkg make-archive`
working, we can use `apkg srcpkg` to build **source package**:

``` mermaid
flowchart TD
    sources[project sources] -- apkg make-archive --> archive
    sources -. apkg srcpkg .-> srcpkg[source package]
    archive -- apkg srcpkg --> srcpkg
```

`apkg srcpkg` needs an **archive** and a **package template** to
build a source package. By default, it creates an archive using `apkg make-archive`
and uses [template](templates.md) based on current distro (`./distro/pkg/$DISTRO`).

Try running `apkg srcpkg` and inspect the output:

``` text
debian-12$> apkg srcpkg

I creating dev source package
I target distro: debian 12
I creating dev archive
I running make_archive_script: scripts/make-archive.sh
I archive created: pkg/archives/dev/foo-v0.1.2.tar.gz
✓ made archive: pkg/archives/dev/foo-v0.1.2.tar.gz
I package style: deb
I package template: distro/pkg/deb
I package archive: pkg/archives/dev/foo-v0.1.2.tar.gz
I package NVR: foo-0.1.2-1
I build dir: pkg/build/srcpkgs/debian-12/foo-0.1.2-1
I result dir: pkg/srcpkgs/debian-12/foo-0.1.2-1
I building deb source package: foo-v0.1.2
I unpacking archive: pkg/archives/dev/foo-v0.1.2.tar.gz
I renderding package template: distro/pkg/deb -> pkg/build/srcpkgs/debian-12/foo-0.1.2-1/foo-v0.1.2/debian
I copying archive into source package: pkg/build/srcpkgs/debian-12/foo-0.1.2-1/foo_0.1.2.orig.tar.gz
I building deb source-only package...
$ dpkg-buildpackage -S -sa -d -nc -us -uc
dpkg-buildpackage: info: source package foo
dpkg-buildpackage: info: source version 0.1.2-1~bookworm
... (more build tool output)
I copying source package to result dir: pkg/srcpkgs/debian-12/foo-0.1.2-1
✓ made source package: pkg/srcpkgs/debian-12/foo-0.1.2-1/foo_0.1.2-1~bookworm.dsc
pkg/srcpkgs/debian-12/foo-0.1.2-1/foo_0.1.2-1~bookworm.dsc
```

Notice

``` text
I renderding package template: distro/pkg/deb -> pkg/build/srcpkgs/debian-12/foo-0.1.2-1/foo-v0.1.2/debian
```

You can inspect the rendered [packaging template](templates.md) and use any
standard distro tools to debug:

``` text
$> ls pkg/build/srcpkgs/debian-12/foo-0.1.2-1/foo-v0.1.2/debian

changelog  compat  control  copyright  files  rules  source
```

Iterate with `apkg srcpkg` and fix issues until it's able to create source
package on distros you want to support.

Once `apkg srcpkg` works, you're able to create **source packages** from your
project sources at any time. Source packages can be used to build binary
packages using wide variety of packaging tools - `apkg build` can help with that
or you can build the packages using tools of your choice.

## build packages

`apkg build` is used to build binary packages from source package.

By default, it invokes `apkg srcpkg` to get a source package directly from
project sources and builds it:

``` mermaid
flowchart TD
    sources[project sources] -- apkg make-archive --> archive
    sources -. apkg srcpkg .-> srcpkg[source package]
    archive -- apkg srcpkg --> srcpkg
    srcpkg -- apkg build --> pkgs[binary packages]
```

!!! info
    `apkg build` uses **direct build** by default - it builds the packages
    directly on the host system without isolation which is the fastest way and
    most starightforward way especially suited for disposable containers/VMs in
    CI/CD or development/packaging machines. This approach also requires build
    dependencies installed on the host system - see `--build-dep` option and
    [apkg build-dep](commands.md#build-dep) command.

    It's **not recommended** to use direct build on production machines as it
    might interfere with the host system in unexpected ways.

    Depending on your pipeline/systems, it might be better to build packages
    using **isolated builders** such as `pbuilder` or `mock` - `apkg build`
    has limited support for this with `--isolated` option.

    Try installing required packages with `apkg system-setup --isolated` and
    running `apkg build --isolated` or `apkg build -I` for short.

    If that doesn't work, consider submitting pull request or simply use source
    package from `apkg srcpkg` and build it as you see fit.


Try running `apkg build` and see what it says. `apkg` should explain clearly
if something is wrong, if that's not the case please do open a
[new issue]({{ new_issue_url }}) as that's a serious usability problem.

Here are examples of successful `apkg build` runs on different distros (with
output filtered using `-L brief` option to success/error messages only):

Debian:

``` text
debian$> apkg build

✓ made archive: pkg/archives/dev/foo-v0.5.1.tar.gz
✓ made source package: pkg/srcpkgs/debian-12/foo-0.5.1-1/foo_0.5.1-1~bookworm.dsc
✓ built 1 packages in: pkg/pkgs/debian-12/foo_0.5.1-1~bookworm
pkg/pkgs/debian-12/foo_0.5.1-1~bookworm/foo_0.5.1-1~bookworm_all.deb
```

Fedora:

``` text
fedora$> apkg build

✓ made archive: pkg/archives/dev/foo-v0.5.1.tar.gz
✓ made source package: pkg/srcpkgs/fedora-40/foo-0.5.1-1/foo-0.5.1-cznic.1.fc40.src.rpm
✓ built 1 packages in: pkg/pkgs/fedora-40/foo-0.5.1-cznic.1.fc40
pkg/pkgs/fedora-40/foo-0.5.1-cznic.1.fc40/foo-0.5.1-cznic.1.fc40.noarch.rpm
```

Arch:

``` text
arch$> apkg build

✓ made archive: pkg/archives/dev/foo-0.5.1.tar.gz
✓ made source package: pkg/srcpkgs/arch/foo-0.5.1-1/PKGBUILD
✓ built 1 packages in: pkg/pkgs/arch/foo-0.5.1-1
pkg/pkgs/arch/foo-0.5.1-1/foo-0.5.1-1-any.pkg.tar.zst
```


To minimize waiting time, `apkg` automatically caches and reuses
archives/source packages/packages produced by individual commands as long
as project is managed by VCS (`git`) and `--no-cache` wasn't supplied.

Re-running the command without changes to project source code results in
`apkg` reusing cached files from previous run:

``` text
debian$> apkg build

✓ reuse cached archive: pkg/archives/dev/foo-v0.5.1.tar.gz
✓ reuse cached source package: pkg/srcpkgs/debian-12/foo-0.5.1-1/foo_0.5.1-1~bookworm.dsc
✓ reuse 1 cached packages
pkg/pkgs/debian-12/foo_0.5.1-1~bookworm/foo_0.5.1-1~bookworm_all.deb
```

With `apkg build` working, you are able to build packages from your project
sources at any time and you can also integrate `apkg` in your CI pipeline to
ensure packaging gets updated alongside code changes.


## clean output directory pkg/

You've probably noticed by now that `apkg` outputs all files
into `pkg/` directory as described in [intro output section](intro.md#output).

You can **delete entire `pkg/` directory** at any time as it only contains
output that can be re-created by re-running `apkg` commands.

In fact, there's a convenience shortcut for this:

```
$> apkg clean

I cleaning apkg output
✓ removed apkg output dir: pkg
```


!!! TODO
    This guide deserves more content ✍🏽

!!! tip
    See [projects using apkg](users.md) 👀
