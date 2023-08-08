# SPDX-License-Identifier: GPL-3.0-or-later

FROM opensuse/leap:15.5

WORKDIR /root
CMD ["/bin/bash"]

# packaging deps
RUN zypper install -y curl git rpm-build python3-pip
# basic deps
RUN zypper install -y python3-beautifulsoup4 python3-setuptools python3-Jinja2 python3-click python3-distro python3-blessings python3-requests python3-toml python3-cached-property
# testing deps
RUN zypper install -y python3-pytest python3-pytest-sugar
# systemd (some tests list services using systemctl)
RUN zypper install -y systemd
