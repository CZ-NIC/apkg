# SPDX-License-Identifier: GPL-3.0-or-later

FROM debian:bookworm
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
    curl \
    debhelper \
    dh-python \
    dpkg-dev \
    git \
    pybuild-plugin-pyproject \
    python3-all \
    python3-hatchling \
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

# add pipx/pip bin dir to $PATH
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# workaround PEP668 breaking pip installs
RUN mkdir -p ~/.config/pip && printf '[global]\nbreak-system-packages = true\n\n' >> ~/.config/pip/pip.conf
