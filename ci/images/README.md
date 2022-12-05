# OCI images for use in CI

- `full/` - images with both apkg and systemd installed (in general, use this for your own CI jobs)
- `systemd/` - basic system images with systemd preinstalled and configured to run first (can be used in non-Docker runtimes)
- `test/` - images for testing apkg - all requirements of tested projects installed, apkg not present
