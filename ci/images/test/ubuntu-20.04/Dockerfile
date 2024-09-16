# SPDX-License-Identifier: GPL-3.0-or-later

FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN apt-get update -qqq
RUN apt-get upgrade -y -qqq

# enable Knot DNS repo (Knot Resolver dep)
RUN apt-get -y -qqq install wget
RUN wget -O - https://pkg.labs.nic.cz/doc/scripts/enable-repo-cznic-labs.sh | bash -s - knot-dns

# packaging deps
RUN apt-get install -y -qqq \
    apt-utils \
    build-essential \
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
    python3-click \
    python3-distro \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
# python deps not available\too old in distro
RUN pip3 install \
    build
