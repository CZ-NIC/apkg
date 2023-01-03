# SPDX-License-Identifier: GPL-3.0-or-later

FROM debian:buster
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN apt-get update -qqq
RUN apt-get upgrade -y -qqq

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
# linting deps
RUN pip3 install \
    flake8 \
    pylint
# basic deps
RUN apt-get install -y -qqq \
    python3-bs4 \
    python3-blessings \
    python3-click \
    python3-cached-property \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
# python deps not available\too old in distro
RUN pip3 install \
    build \
    distro
# doc deps
RUN pip3 install \
    mkdocs \
    mkdocs-material \
    mkdocs-macros-plugin \
    pymdown-extensions
