# SPDX-License-Identifier: GPL-3.0-or-later

FROM ubuntu:26.04
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
    pybuild-plugin-pyproject \
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
    python3-blessed \
    python3-bs4 \
    python3-build \
    python3-click \
    python3-distro \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml \
    python3-tomli-w \
    python3-yaml

# add pipx/pip bin dir to $PATH
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# workaround PEP668 breaking pip installs
RUN mkdir -p ~/.config/pip && printf '[global]\nbreak-system-packages = true\n\n' >> ~/.config/pip/pip.conf
