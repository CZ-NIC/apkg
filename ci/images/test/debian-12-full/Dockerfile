# SPDX-License-Identifier: GPL-3.0-or-later

FROM debian:bookworm
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
    python3-setuptools \
    pipx
# testing deps
RUN apt-get install -y -qqq \
    python3-pytest \
    python3-pytest-sugar
# basic deps
RUN apt-get install -y -qqq \
    python3-blessings \
    python3-bs4 \
    python3-build \
    python3-click \
    python3-distro \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
# linting deps
RUN pip3 install --break-system-packages \
    flake8 \
    pylint \
    ruff
# doc deps
RUN pip3 install --break-system-packages \
    mkdocs \
    mkdocs-material \
    mkdocs-macros-plugin \
    pymdown-extensions
