# apkg installation

`apkg` is going to provide native distro packages once mature.

For now you need to

* [install requirements](#requirements) (just `pip` and `setuptools`)

and then choose howto install:

* [install from PyPI](#install-from-pypi-recommended) - **recommended**
* [install from source](#install-from-source)


## requirements

You need **Python >= 3.6** and `pip`.

**Python 3.5** is EOL but it's unofficially supported on best-effort basis in
apkg until Debian 9 Stretch LTS EOL June 30, 2022.

Install following **system packages** using your system's package manager:

* `python3-pip`
* `python3-setuptools`

=== "Debian, Ubuntu"
    ```
    apt-get install -y python3-pip python3-setuptools
    ```

=== "Fedora, CentOS 8+"
    ```
    dnf install -y python3-pip python3-setuptools
    ```

=== "CentOS 7"
    ```
    yum install -y python3-pip python3-setuptools
    ```

=== "openSUSE"
    ```
    zypper install -y python3-pip python3-setuptools
    ```

=== "Arch"
    ```
    pacman -Sy python-pip python-setuptools
    ```

Other python requirements should be **handled automatically**, they are
listed and briefly explained in {{ 'requirements.txt' | file_link }}.

Python modules needed to build `apkg` docs are listed in
{{ 'doc-requirements.txt' | file_link }}.


## install from PyPI (recommended)

In order to support widest variety of distros and their releases while leveraging latest and greatest python modules, `apkg` is
primarily distributed through
[Python Package Index (PyPI)](https://pypi.org/project/apkg/)
using `pip`, `pipx`, or other similar tool of your choice.

Make sure you've installed `python3-pip` using your distro package manager as
described in [requirements](#requirements).


### user install from PyPI

To ensure **any** version of apkg is installed for current user:

```
pip3 install --user apkg
```

Modern `pip` automatically appends `--user` so `pip3 install apkg` should be fine most of the time.

To ensure **latest** version of apkg is installed for current user use `-U`/`--upgrade`:

```
pip3 install --user -U apkg
```

If you prefer to install apkg into isolated virtualenv and only expose `apkg` script, consider using `pipx` instead:

```
pip3 install pipx
pipx install apkg
```

Depending on your `$PATH`, `apkg` script may be available. If it isn't you can
always invoke apkg module:

```
python3 -m apkg build -b
```


### automation / CI / DevOps install from PyPI

For automated usage in CI and other DevOps systems it's recommended to use:

```
pip3 install apkg
```

which should generally work in any use case including:

* install as normal system user
* install as root (containers)
* install in virtualenv

If you want **latest and greatest apkg**, use `--upgrade`/`-U`:

```
pip3 install -U apkg
```

If you prefer to use a **single tested version** of `apkg` and be completely independent on latest releases, you can pin apkg to a specific version, for example:

```
pip3 install apkg==0.0.4
```

Depending on your `$PATH`, `apkg` script may be available. If it isn't you can
always invoke apkg module

```
python3 -m apkg build -b
```

## install from source

Make sure [requirements](#requirements) are installed and you're in the top `apkg` source dir:

```
git clone https://gitlab.nic.cz/packaging/apkg
cd apkg
```

Then choose one of installation methods below:


### user install from source

Fastest and recommended way to install from source for CLI usage without
affecting the rest of your system is to use
[pipx](https://pipxproject.github.io/pipx/installation/):

```
pip3 install pipx
pipx install .
```

This installs `apkg` into `virtualenv` without affecting rest of your system
while only exposing `apkg` CLI script.

`pipx install` also features convenient `--editable` mode.

If you're using `apkg` python module or you don't want to use `pipx`, you can
use local user `pip install`:

```
pip3 install --user .
```

Or the old-fashioned equivalent through `setup.py` but that's using
`easy_install` which is worse than `pip`:

```
python3 setup.py install --user
```


### editable/develop install

For development it's nice when source changes immediately apply and that
can be done with editable/develop install.

Old-fashioned and well tested develop install using `setup.py` has the advantage of making `apkg` module available to other python modules:

```
python3 setup.py develop --user
```

This creates a link in `~/.local/lib/python3.X/site-packages/apkg.egg-link`
and also installs `apkg` script into `~/.local/bin` so make sure you have
`~/.local/bin` in your `$PATH`, possibly before system `bin` paths to override
`apkg` scripts provided by system packages.

When you need CLI only, it's recommended to use `pipx` instead in `--editable` mode:

```
pip3 install pipx
pipx install -e .
```

Upstream python discussions recommend `pip3 install --editable .` but that has
the fatal flaw of currently not working with local `--user` install. You can
use it inside disposable container or a VM but I'd never taint my system
python installation with a global install like that.


### virtualenv install from source

If you don't want `apkg` installation to affect your system but don't want
to/can't use `pipx`, you can use `virtualenv` directly (`python3-venv`
package usually):

```
git clone https://gitlab.nic.cz/packaging/apkg
cd apkg
virtualenv3 venv
source venv/bin/activate
python3 setup.py install
apkg
```

You can enter the `venv` later/from other terminals by

```
source apkg/venv/bin/activate
```


With `apkg` installed, check out [packaging guide](guide.md) 📑
