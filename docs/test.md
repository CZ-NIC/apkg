# apkg packaging tests

`apkg` provides a simple packaging tests runner based on Debian [autopkgtest]
([DEP8]) with [extra](#tests-extras) features to allow cross-distro operation:

```
apkg test
```

`apkg test` assumes the packages in question are already installed on the
testing system. They can be installed by `apkg install` or by any other means.

`apkg test` can be used independently on other `apkg` features,
it only requires `distro/tests` directory.

To get information about tests, use `-i`/`--info` argument:

```
apkg test --info
```

{{ added_in_version('0.4.0', compat=3) }}


## tests directory

`distro/tests` directory contains all test files and metadata as seen in `debian/tests`, for example:

```
distro/tests
├── control
├── test-client.sh
├── test-server.sh
└── test-version.sh
```

Tests are run in project root.


## control - tests metadata file

Packaging tests and their dependencies are defined in a metadata file called
`control` with syntax as described in [autopkgtest], for example:

```
{{ 'examples/pkgtests-basic/distro/tests/control' | file_raw }}
```

By default, it resides in `distro/tests/control`, but you can also provide
per-distro `control` using [tests extras](#tests-extras).

Run a single test from `distro/tests`:

```
Tests: test-foo.sh
```

Run multiple tests from `custom/tests` tests directory:

```
Tests: test-foo.sh test-bar.sh test-kek.sh
Tests-Directory: custom/tests
```

Run a shell command:

```
Test-Command: foo --help
```

Run tests as root (use `sudo` if not root):

```
Tests: test-root-foo.sh test-root-bar.sh
Restrictions: needs-root

Test-Command: echo `whoami`
Restrictions: needs-root
```

Define tests dependencies (distro packages to install):

```
Tests: test-a test-b test-c
Depends: tree, atool

Test-Command: foo
Depends: foo
```


## tests extras

**tests extras** is an apkg-specific extension of [autopkgtest] which allows the
reuse of packaging tests across different distros.

Optional `distro/tests/extra` directory contains individual **extras** in
separate directories.

Each **extra** directory contains extra files to be **templated using jinja** and **copied over** a
test-specific instance of `distro/tests` providing an universal way to control
and even modify tests based on target [distro](distro.md).

To list all extras and other useful information, use

```
$> apkg test --info

tests path:         distro/tests (exists)
tests extras path:  distro/tests/extra (exists)
tests extras:
    arch: pkgstyle default: arch
    deb: pkgstyle default: ubuntu | debian | linuxmint | raspbian
    rpm: pkgstyle default: fedora | centos | rocky | rhel | opensuse | ...

testing distro:     arch rolling
tests control:      distro/tests/extra/arch/control (exists)
tests extra:        distro/tests/extra/arch

tests:
    test-client.sh
    test-server.sh
    test-arch-specific.sh
        Depends: pacman
```


### extra files syntax

`apkg` uses [jinja] the great python templating engine with magic
[distro](distro.md#distro-in-templates) variable available.

Example `control` template:

```jinja
{{ 'examples/pkgtests-all-template/distro/tests/extra/all/control' | file_raw }}
```

`include` and `include_raw` tags are also available, see
[reusing code in templates](templates.md#reusing-code-in-templates).

You can view the rendered contents of active tests `control` file using `-c`/`--show-control`:

```
$> apkg test --show-control
$> apkg test --show-control --distro debian-12
$> apkg test -c -d fedora-38
```


### extra selection

A tests extra (from `distro/tests/extra/`) is selected and used based on a
target [distro](distro.md), taking [distro aliases](distro.md#distro-aliases)
into consideration much like
[template selection](templates.md#template-selection).

To allow full control over tests, `apkg` provides 4 types of tests extra
selection mechanisms (described below) which can be combined as needed.

You can also supply `apkg test` with `--info` and `--distro` arguments to check
which template gets selected on a particular distro:

```
$> apkg test --info --distro debian-11
...
testing distro:     debian 11
tests control:      distro/tests/extra/deb/control (exists)
tests extra:        distro/tests/extra/deb
```


### pkgstyle default extra

The simplest and most general type of tests extra that is used for any distro
supported by selected [packaging style](pkgstyles.md).

Simply name the template directory in `distro/tests/extra/` the same as the
desired [packaging style](pkgstyles.md) such as `deb`, `rpm`, `nix`, or `arch`
and it will be used as a default for all distros supported by that style.


### distro-specific extra

Extras in `distro/tests/extra/` which aren't named as an existing [packaging
style](pkgstyles.md) are considered to be **distro-specific**. They are selected by
`apkg` based on their name.

In simplest case, distro-specific extra is only selected when target distro
matches its name:

* `debian`: any Debian version (but not clones)
* `ubuntu`: any Ubuntu version
* `fedora`: any Fedora version

Additionally, specific distro version can be requested using `-` (dash) separator:

* `debian-12`: Debian 12
* `ubuntu-22.04`: Ubuntu 22.04
* `fedora-38`: Fedora 38

Only numeric versions are supported, codenames such as `buster` or `Focal Fosa`
won't work.


### distro alias extra

Distro alias extras provide full control over their selection based on
[distro aliases](distro.md#distro-aliases)
defined in [config](config.md#distroaliases).

When a tests extra name matches a defined
[distro alias](distro.md#distro-aliases),
its distro rules are used to select the extra.

For example to use `deb-old` distro alias defined as follows:

```toml
[[distro.aliases]]
name = "deb-old"
distro = ["debian < 9", "ubuntu < 20.04"]
```

simply create `distro/tests/extra/deb-old` extra and `apkg` will select it based on
supplied distro rule - on Debian versions older than 9 and on Ubuntu versions
older than 20.04.


### default fallback extra (all)

The special `all` tests extra in `distro/tests/extra/all` is used as a fallback
when no other extra is selected.

Use this if you need templating in default test files. If you don't need
templating, use inline `distro/tests/control` instead.

You can use `all` extra with templating to have a single `control` file for
different distros:

```jinja
{{ 'examples/pkgtests-all-template/distro/tests/extra/all/control' | file_raw }}
```


## Debian autopkgtest compatibility

`apkg test` aims to reuse and share Debian packaging tests without modification,
but it doesn't feature full [autopkgtest] compatibility.

### supported autopkgtest features

* define tests in `control` format as seen in Debian tests (`debian/tests/control`)
* define tests using `Tests` or `Test-Command`
* override tests dir using `Tests-Directory`
* define test dependencies using `Depends`
* tests marked with `Restrictions: needs-root` are run with sudo when user isn't root
* tests marked with `Restrictions: flaky` are skipped on fail
* tests may return code 77 to SKIP (by default, no `skippable` needed)

### autopkgtest differences

* `Restrictions: allow-stderr` is enabled by default as stderr is often used for
  logging without indicating error
* `Restrictions: skippable` is enabled by default allowing tests to indicate
  SKIP by returning code 77 in order to prevent redundant `skippable`
  entries in `control` files


## test command examples

Run tests:

    apkg test

Run tests with verbose/brief logging:

    apkg -L verbose test
    apkg -L brief test

Run tests filtered by regex:

    apkg test -k pattern

Display tests info:

    apkg test --info

Display tests info for a distro:

    apkg test --info --distro debian-11

List active tests:

    apkg test --list-tests

List filtered tests:

    apkg test -l -k pattern

Display test `control` file contents:

    apkg test --show-control

Install test deps and run tests:

    apkg test --test-dep

Install test deps:

    apkg test-dep

List test deps:

    apkg test-dep --list

Install both build and test deps with one command:

    apkg build-dep --test-dep


[autopkgtest]: https://salsa.debian.org/ci-team/autopkgtest/raw/master/doc/README.package-tests.rst
[DEP8]: https://dep-team.pages.debian.net/deps/dep8/
[jinja]: https://jinja.palletsprojects.com/en/3.0.x/templates/
