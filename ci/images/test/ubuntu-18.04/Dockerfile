# SPDX-License-Identifier: GPL-3.0-or-later

FROM ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN apt-get update -qqq
RUN apt-get upgrade -y -qqq

# install add-apt-repository
RUN apt-get install -y -qqq software-properties-common
# add Knot DNS repo (needed by Knot Resolver as build dep)
RUN add-apt-repository ppa:cz.nic-labs/knot-dns-latest
# refresh repos
RUN apt-get update -qqq

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
    python3-pytest
# basic deps
RUN apt-get install -y -qqq \
    python3-blessings \
    python3-click \
    python3-jinja2 \
    python3-packaging \
    python3-toml
# python deps not available\too old in distro
RUN pip3 install \
    beautifulsoup4 \
    build \
    distro \
    cached_property
