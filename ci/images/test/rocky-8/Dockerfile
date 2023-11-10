# SPDX-License-Identifier: GPL-3.0-or-later

FROM rockylinux/rockylinux:8
ENV LC_ALL=C.UTF-8

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN dnf upgrade -y
# get dnf plugins
RUN dnf install -y dnf-plugins-core
# enable PowerTools
RUN dnf config-manager --set-enabled powertools
# enable EPEL
RUN dnf install -y epel-release
# update repos
RUN dnf update -y

# packaging deps
RUN dnf install -y \
    git \
    rpm-build \
    python3-pip
# basic deps
RUN pip3 install \
    beautifulsoup4 \
    blessings \
    cached-property \
    click \
    distro \
    jinja2 \
    packaging \
    requests \
    toml
# testing deps
RUN pip3 install \
    pytest
