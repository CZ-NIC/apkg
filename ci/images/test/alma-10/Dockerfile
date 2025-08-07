# SPDX-License-Identifier: GPL-3.0-or-later

FROM almalinux:10-kitten

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN dnf upgrade -y
# get dnf plugins
RUN dnf install -y dnf-plugins-core
# enable crb (PowerTools)
RUN dnf config-manager --set-enabled crb
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
RUN dnf install -y \
    python3-beautifulsoup4 \
    python3-cached-property \
    python3-click \
    python3-distro \
    python3-jinja2 \
    python3-packaging \
    python3-pyyaml \
    python3-requests \
    python3-tomli-w
# not available from distro packages
RUN pip3 install \
    blessed
# testing deps
RUN pip3 install \
    pytest
