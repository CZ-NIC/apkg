# apkg quick start

This is a short guide on howto use apkg with projects that are already set up to
use it.


## host system

TODO: containers vs production machines


## install apkg

First of all, [install apkg](install.md).


## get project sources

I'll use [BIRD](https://gitlab.nic.cz/labs/bird) as an example project.

Start by cloning the repo of a project using apkg and entering it.

```
git clone https://gitlab.nic.cz/labs/bird.git
cd bird
```

## status check

```
$ apkg status

project name:            bird
project base path:       /home/jru/src/bird
project VCS:             git
project config:          distro/config/apkg.toml (exists)
project compat level:    3 (current)
package templates path:  distro/pkg (exists)
package templates:
    deb: deb pkgstyle default: debian | linuxmint | pop | raspbian | ubuntu
    rpm: rpm pkgstyle default: almalinux | centos | fedora | opensuse | oracle | pidora | rhel | rocky | scientific

current distro: debian 12 / Debian GNU/Linux 12 (bookworm)
    package style: deb
    package template: distro/pkg/deb
```


## system setup

```
apkg system-setup
```


## install build dependencies

```
apkg build-dep
```


## build source package


```
apkg srcpkg
```


## build packages

```
apkg build
```


## optional: install packages

```
apkg install
```


## optional: run packaging tests

```
apkg test --test-dep
```
