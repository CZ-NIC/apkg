# SPDX-License-Identifier: GPL-3.0-or-later

FROM fedora:42

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN dnf upgrade -y

# packaging deps
RUN dnf install -y \
    git \
    rpm-build \
    python3-pip \
    pipx
# basic deps
RUN dnf install -y \
    python3-beautifulsoup4 \
    python3-blessed \
    python3-click \
    python3-distro \
    python3-jinja2 \
    python3-packaging \
    python3-pyyaml \
    python3-requests \
    python3-tomli-w
# testing deps
RUN dnf install -y \
    python3-pytest \
    python3-pytest-sugar
