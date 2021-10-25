# apkg news


## apkg 0.3.0

Released 2021-11-??

## NEXT RELEASE (TBD)


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
