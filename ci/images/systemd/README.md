# per-distro images with systemd

## Why?

As a lightweight alternative to VMs. Systemd is necessary for some integration
/ packaging tests utilized by Knot Resolver.

## What

Images are ready-to-use with any OCI container runner that supports systemd
(podman, LXC, ...). They are configured with systemd and you get auto
logged in as root.

Images are pre-installed to be used as containers for GitLab Runner with custom
LXC executor (this repo).

## Maintenance

To avoid copying common files, they are placed directly in `images/` directory.
Consequently, it needs to be used as the context directory for the build.

Utility scripts can be used to build, push or update the container images.

```
$ ./build.sh debian-11    # builds a debian-11 image locally
$ ./push.sh debian-11     # pushes the local image into target registry
$ ./update.sh debian-11   # utility wrapper that both builds and pushes the image
$ ./update.sh */          # use shell expansion of dirnames to update all images
```
