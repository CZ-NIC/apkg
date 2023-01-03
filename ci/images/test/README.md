# apkg CI images

## build image

use `build.sh` to build docker image, for example:

```
./build.sh debian-10
```

## push (upload) image into apkg CI

you need to **login** first:

```
$ docker login registry.nic.cz
```

then you can use `push.sh` script:

```
./push.sh debian-10
```

## build & push images

use `update.sh` wrapper to build and push multiple images
using `build.sh` and `push.sh` scripts described above:

```
./update.sh debian-10 debian-11 rocky-8
```
