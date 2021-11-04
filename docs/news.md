# apkg news


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
