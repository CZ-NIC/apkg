FROM registry.nic.cz/packaging/apkg/systemd/fedora-41

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN dnf upgrade -y

# packaging deps
RUN dnf install -y \
    git \
    rpm-build \
    python3-setuptools \
    python3-pip
# basic deps
RUN dnf install -y \
    python3-beautifulsoup4 \
    python3-blessings \
    python3-click \
    python3-distro \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
# gdb not pulled in on Fedora 41 leading to build failures
RUN dnf install -y gdb
# install stable apkg from PyPI
RUN python3 -m pip install apkg
RUN apkg --version
