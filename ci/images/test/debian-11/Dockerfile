# SPDX-License-Identifier: GPL-3.0-or-later

FROM debian:bullseye
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN apt-get update -qqq
RUN apt-get upgrade -y -qqq

# configure repository with Knot Resolver dependencies
RUN apt-get -y -qqq install apt-transport-https lsb-release ca-certificates wget curl gnupg2
RUN sh -c 'echo "deb http://download.opensuse.org/repositories/home:/CZ-NIC:/knot-resolver-build/Debian_10/ /" > /etc/apt/sources.list.d/home:CZ-NIC:knot-resolver-build.list'
RUN sh -c 'curl -fsSL https://download.opensuse.org/repositories/home:CZ-NIC:knot-resolver-build/Debian_10/Release.key | gpg --dearmor > /etc/apt/trusted.gpg.d/home_CZ-NIC_knot-resolver-build.gpg'
RUN apt-get update -qqq

# packaging deps
RUN apt-get install -y -qqq \
    apt-utils \
    build-essential \
    curl \
    debhelper \
    dh-python \
    dpkg-dev \
    git \
    python3-all \
    python3-pip \
    python3-setuptools
# testing deps
RUN apt-get install -y -qqq \
    python3-pytest \
    python3-pytest-sugar
# basic deps
RUN apt-get install -y -qqq \
    python3-bs4 \
    python3-blessings \
    python3-build \
    python3-click \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
