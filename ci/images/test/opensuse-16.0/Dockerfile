# SPDX-License-Identifier: GPL-3.0-or-later

FROM opensuse/leap:16.0

WORKDIR /root
CMD ["/bin/bash"]

# upgrade to latest
RUN zypper --non-interactive dup

# packaging deps
RUN zypper --non-interactive install \
    curl \
    git \
    rpm-build \
    python3 \
    python3-pip

# basic deps
RUN zypper --non-interactive install \
    python313-beautifulsoup4 \
    python313-setuptools \
    python313-Jinja2 \
    python313-click \
    python313-distro \
    python313-blessings \
    python313-requests \
    python313-toml \
    python313-cached-property \
    python313-PyYAML

# testing deps
RUN zypper --non-interactive install \
    python3-pytest

# systemd (some tests list services using systemctl)
RUN zypper --non-interactive install \
    systemd
