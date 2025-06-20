# apkg news

## apkg 0.6.1

Released 2025-06-20

### Fixes

- reintroduce `toml` dep for older systems with Python < 3.11


## apkg 0.6.0

Released 2025-06-19

### Compat Level 5 News

- new [apkg lint](commands.md#lint) command to invoke native distro linters (`lintian`, `rpmlint`)
- improved [apkg system-setup](commands.md#system-setup) command including new `--lint` option to install linting deps
- new [apkg info apkg-deps](commands.md#info-apkg-deps) command to show dependencies colored for easy debugging
- new [distro_like](templatevars.md#apkgtemplatevarsdistro_like) template variable module for detecting similar distros
- `rpm`: evaluate RPM macros using `rpmspec` if available
    - `apkg` now works with `.spec` files using complex macros including macros in `Name`
- [template variables](templatevars.md) are now always passed when rendering templates
    - some `pkgstyle` functions previously rendered templates directly without
      template variables which lead to errors in special cases
- `apkg.templatevars.debseries` module was renamed to `deb_series` for consistency
    - old `debseries` module is still supported for the time being, it emits a warning when used

### Improvements

- Python 3.13 is now [supported](platforms.md) and tested in CI
- new distros are now [supported](platforms.md) and tested in CI:
    - Debian 13 Trixie
    - Ubuntu 25.04 Plucky Puffin and 24.10 Oricular Oriole
    - Enterprise Linux 10: RHEL 10, AlmaLinux 10, Rocky 10
    - Fedora 42 and 41
- lighten dependencies:
    - drop `hatchling` build dep in favor of `setuptools`
    - drop `dunamai` build dep in favor of custom solution
- improved handling of unreleased / versionless distros, including Debian testing, unstable, experimental
- new `util.toml` module for robust runtime TOML libs selection
    - supports `tomllib` (standard library since Python 3.11), `tomli`, `toml`,
    `tomlkit` modules for TOML loading
    - supports `tomli_w`, `toml`, `tomlkit` for TOML dumping
- improved logging of function names when using `-L verbose` and `-L debug`
- big [packaging guide](guide.md) upgrade
    - new fancy Mermaid [diagrams](guide.md#graphical-diagram-of-apkg-workflow)
    - updated workflow with `install`, `test`, `lint` commands
    - new `added_in_version` macro to provide consistent version / compat information


## apkg 0.5.1

Released 2024-06-24

### Fixes

- update `requires-python` to `>=3.6` to enable installation on old systems
- small docs fixes

## apkg 0.5.0

Released 2024-04-03

### Compat Level 4 News

- new [custom template variables](templatevars.md) support
    - new [template.variables](config.md#templatevariables) config section
    - extend `apkg status` command with template variables sources status
    - new `apkg info template-variables` command
        - show all template variables by default
        - show custom variables per source with `--custom`
- `deb` pkgstyle: include `*.changes` files in `srcpkg`/`build` output
    - many debian tools and workflows require `*.changes` files - comply
- fix incorrect parsing of single compnent versions (`1`, `20240101`, etc.)

### Improvements

- updated and overhauled [installation docs](install.md)
- new [platform support docs](platforms.md) with detailed information
  about Python versions and distros supported by apkg


## apkg 0.4.2

Released 2023-08-08

### Fixes

- re-introduce `cached_property` requirement to support Python <= 3.7


## apkg 0.4.1

Released 2023-07-19

### Improvements

- use modern python packaging through `pyproject.toml`
    - use `hatchling` for build
    - use PEP440 compatible versioning
    - support legacy `setuptools` for backward compat
    - improve archive and sdist generation
    - improve Debian packaging (pyproject build on Debian 12 and newer)
    - rename distro package to just `apkg`
    - support both `blessed` (maintained fork) and `blessings` for colors
- `arch` pkgstyle improvements:
    - support Manjaro
    - only install `--needed` distro packages
    - require base-devel for `apkg system-setup`
- `deb` pkgstyle improvements:
    - support Pop_OS! (Ubuntu derivative)
    - only require build-essential (not devscripts) on `apkg system-setup`
    - sort `SUPPORTED_DISTROS` alphabetically

### Fixes

- fix distro alias ordering during template selection
- handle exceptions introduced by upstream `packaging.version` changes


## apkg 0.4.0

Released 2022-07-18

### Compat Level 3 News

- new [apkg test](test.md) packaging tests runner based on Debian `autopkgtest`
- new [apkg info](commands.md#info) command with subcommands to display various info:
    - `apkg info cache`: show apkg cache contents
    - `apkg info config`: show apkg project configuration
    - `apkg info distro`: show current distro information
    - `apkg info distro-aliases`: list available distro aliases
    - `apkg info pkgstyles`: list available packaging styles
    - `apkg info upstream-version`: show detected project upstream version
- new [apkg clean](commands.md#clean) command to clean output dir `pkg/`
    - `apkg clean`: remove apkg output directory `pkg/`
    - `apkg clean --cache`: remove apkg cache file `pkg/.cache.json`
    - `apkg clean --hard`: HARD RESET project from VCS and remove extra files
- new `include_raw` tag available from [templates](templates.md#reusing-code-in-templates)
    to include files without templating
- support for AlmaLinux in `rpm` pkgstyle (`almalinux`)

### Improvements

- command runner was refactored using `asyncio`
    - `run()` can `tee` command output - it's **finally** possible to both read
      and display `stdout` at the same time resulting in better real-time/log
      output and debugging when invoking external commands
    - `run()` logging was fixed and improved, use `-L verbose` to see all commands
      run in the background
- [cache](cache.md) was refactored to be more flexible and reliable in edge cases
    - cache false positives should no longer appear
    - individual cache targets can be [configured](config.md#cache) indpendently
    - only [source cache](cache.md#source-cache) is disabled when VCS isn't available
    - new [cache docs](cache.md) as well as updated other docs with useful info and links
- new minimal example project `examples/minimal-no-git`

### Fixes

- fix package manager detection in `rpm` pkgstyle
- parse `makedepends` as well as `depends` in `arch` pkgstyle
- fix `--archive`/`--upstream` operation in `build-dep`
- don't install 0 build deps
- use temporary dir for archive unpack (more reliable)


## apkg 0.3.1

Released 2021-11-04

### Fixes

- follow symlinks when rendering templates


## apkg 0.3.0

Released 2021-11-03

### Compat Level 2 News

- better [distro](distro.md) handling
    - [distro rules](distro.md#distro-rules) to specify particular distro version range
    - [distro aliases](distro.md#distro-aliases) to conveniently refer to custom distro sets
    - magic `distro` variable [in templates](distro.md#distro-in-templates) for dynamic templating
- new flexible [template selection](templates.md#template-selection)
- new config options to control special files in templates using patterns:
    - [template.ignore_files](config.md#templateignore_files) to ignore/skip files
    - [template.plain_copy_files](config.md#templateplain_copy_files) to copy files without templating
- support Jinja's [include](https://jinja.palletsprojects.com/en/3.0.x/templates/#include) tag
- new `now` template variable available in `deb` and `rpm` pkgstyles (for changelog dates)

### Improvements

- new `apkg compat` command and [compat docs](compat.md)
- `apkg` will refuse to work with projects with newer compat level
- new minimal templating example `examples/templates`
- sort `apkg srcpkg` output for determinism
- update and extend docs (new pages: [compat](compat.md), [distro](distro.md), [users](users.md))

### Fixes

- fix false positive cache hits in special cases
- CI fixes and improvements


## apkg 0.2.0

Released 2021-07-13

### Improvements

- support **Rocky Linux** through `rpm` pkgstyle
- support **Nix** through new `nix` pkgstyle
- align `apkg install` with other commands and extend functionality
- extend CI to test `apkg install` on supported distros
- extend CI with new integration tests against apkg itself to ensure full apkg
  pipeline (including `install`) works on supported distros
- improve apkg archive creation script `make-archive.sh`
- remove problematic `htmllistparse` dependency in favor of using
  `beautifulsoup4` directly

### Fixes

- handle unset `$PWD` when running external commands
- fail on unexpected input files in `srcpkg`
- fix docs build

### Incompatible Changes ⚠

- `apkg install` now works on project source by default like other commands
  (`srcpkg`, `build`). Old behavior of installing custom packages is available
  through `-C`/`--custom-pkgs` option.
- `-i`/`--install-dep` option of `apkg build` was renamed to `-b`/`--build-dep`
  to remove ambiguity. Old alias still works but it's deprecated an will be
  removed in future versions.


## apkg 0.1.1

Released 2021-06-09

- first apkg beta release
