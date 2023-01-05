# apkg LXC images

These are per-distro LXC images based on `systemd` images..

Unlike native gitlab docker, LXC can run systemd and these images contain it
so you can

    systemctl start foo

etc.

Use those images from your `Dockerfile`:

    FROM registry.nic.cz/packaging/apkg/lxc/debian-11

## build image

use `build.sh` to build docker image, for example:

```
./build.sh debian-11
```

## push (upload) image into apkg CI

you need to **login** first:

```
$ docker login registry.nic.cz
```

then you can use `push.sh` script:

```
./push.sh debian-11
```

## build & push images

use `update.sh` wrapper to build and push multiple images
using `build.sh` and `push.sh` scripts described above:

```
./update.sh debian-10 debian-11 ubuntu-22.04
```
