# apkg installation

`apkg` is going to provide native distro packages once mature.

For now you need to

* [install requirements](#requirements)

and then choose howto install:

* [install from PyPI](#install-from-pypi) - **recommended**
* [install from source](#install-from-source)


## requirements

apkg needs **Python**.

apkg [0.5.1](news.md#apkg-051) has been tested to work on all Python versions
between **3.6** and **3.12**.

See [apkg Python support](platforms.md#python-support) for detailed information
about supported Python versions.

To install apkg, you **need** [pipx], `pip`, or other compatible Python package
installer.

Further apkg requirements are **handled automatically** by the installer.
They're listed and briefly explained in {{ 'requirements.txt' | file_link }}.

Python modules needed to build apkg docs are listed in
{{ 'doc-requirements.txt' | file_link }}.


### installer: pipx

[pipx] is a **recommended** tool for installing apkg into virtualenv and providing
`apkg` command without disrupting host system.


**Install `pipx` package** using distro package manager:

=== "Debian, Ubuntu"
    ```
    apt install -y pipx
    ```

=== "Fedora, EL"
    ```
    dnf install -y pipx
    ```

=== "openSUSE"
    ```
    zypper install -y python-pipx

    # on openSUSE Leap 15, it's better to use newer Python:
    zypper install -y python311-pipx
    ```

=== "Arch, Manjaro"
    ```
    pacman -Sy python-pipx
    ```

If your distro doesn't [provide][repology-pipx] `pipx`,
consult [pipx installation docs](https://pipx.pypa.io/stable/installation/) and/or
consider **installing `pipx` using `pip`**:

```
pip3 install pipx
```

**Ensure `pipx` scripts path is in your PATH** environment variable:

```
pipx ensurepath
```

Or add `~/.local/bin` to your `$PATH` manually.


### installer: pip

[PEP 668] makes it harder to disrupt
[Externally Managed Python Environments](https://packaging.python.org/en/latest/specifications/externally-managed-environments/)
(such as those provided by linux distros) by requiring `--break-system-packages`
flag on `pip install`.

Even `--user` installation now requires this flag on modern distros and users
are advised to use isolated virtualenvs as not to break their Python environment.

[pipx] is a recommended tool for installing apkg into virtualenv and providing the
`apkg` command without disrupting host system, see
[installer: pipx](#installer-pipx).

As a rule of thumb, if a distro is new enough to complain about [PEP 668], it's new enough to run `pipx`. It's likely to be already packaged in [distro repos][repology-pipx].

Valid use cases for using `pip` instead of `pipx`:

* installing apkg into virtualenv
* installing apkg python module for other consumers
* installing apkg on old/ancient distros without `pipx` support
* installing apkg while reusing system python packages

**Install `pip` package** using distro package manager:

=== "Debian, Ubuntu"
    ```
    apt-get install -y python3-pip
    ```

=== "Fedora, EL"
    ```
    dnf install -y python3-pip
    ```

=== "openSUSE"
    ```
    zypper install -y python3-pip
    ```

=== "Arch, Manjaro"
    ```
    pacman -Sy python-pip
    ```


## install from PyPI

In order to support widest variety of distros and their releases while
leveraging latest and greatest python modules, `apkg` is primarily distributed
through [Python Package Index (PyPI)](https://pypi.org/project/apkg/) using
`pipx`, `pip`, or other similar tool of your choice.


**Install apkg:**

=== "pipx"
    ```
    pipx install apkg
    ```

=== "pip"
    ```
    pip3 install apkg
    ```

**Install specific apkg version:**

=== "pipx"
    ```
    pipx install apkg==0.4.2
    ```

=== "pip"
    ```
    pip3 install apkg==0.4.2
    ```

**Upgrade apkg to latest version:**

=== "pipx"
    ```
    pipx upgrade apkg
    ```

=== "pip"
    ```
    pip3 install --upgrade apkg
    ```


## install from source

Make sure [requirements](#requirements) are met.


**Install apkg from remote git repo:**

=== "pipx"
    ```
    pipx install git+https://gitlab.nic.cz/packaging/apkg.git
    ```

=== "pip"
    ```
    pip3 install git+https://gitlab.nic.cz/packaging/apkg.git
    ```

!!! NOTE
    This installs the development version of apkg from `master` branch with
    unreleased features and fresh bugs.


**Get apkg sources:**

```
git clone https://gitlab.nic.cz/packaging/apkg
cd apkg
```

You can switch to a particular branch:

```
git checkout juicy-new-feature
```

Or checkout a specific version tag:

```
git checkout v0.4.2
```

**Install apkg from sources:**

=== "pipx"
    ```
    pipx install .
    ```

=== "pip"
    ```
    pip3 install .
    ```

=== "setup.py"
    ```
    # OBSOLETE LEGACY COMPATIBILITY FOR ANCIENT SYSTEMS
    # don't use this unless you absolutely must
    python3 setup.py install
    ```

Alternatively, add `--editable` option to enable
**editable installation** convenient for apkg development:

=== "pipx"
    ```
    pipx install --editable .
    ```

=== "pip"
    ```
    pip3 install --editable .
    ```

=== "setup.py"
    ```
    # OBSOLETE LEGACY EXAMPLE
    # if you were used to do this, use pipx install --editable
    python3 setup.py develop --user
    ```

`--editable` mode allows to immediately test changes to apkg source code.



With `apkg` installed, check out [packaging guide](guide.md) 📑


[PEP 668]: https://peps.python.org/pep-0668/
[pipx]: https://pipx.pypa.io/
[repology-pipx]: https://repology.org/project/pipx/versions
