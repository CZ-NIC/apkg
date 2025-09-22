# SPDX-License-Identifier: GPL-3.0-or-later

FROM opensuse/leap:15.6

WORKDIR /root
CMD ["/bin/bash"]

# upgrade to latest
RUN zypper dup -y
# packaging deps
RUN zypper install -y curl git rpm-build python3-pip
# basic deps (default ancient python 3.6)
RUN zypper install -y python3-beautifulsoup4 python3-setuptools python3-Jinja2 python3-click python3-distro python3-blessings python3-requests python3-toml python3-cached-property python3-PyYAML
# testing deps
RUN zypper install -y python3-pytest
# python 3.11 deps
RUN zypper install -y python311-pip python311-pytest python311-beautifulsoup4 python311-setuptools python311-Jinja2 python311-click python311-distro python311-blessings python311-requests python311-toml python311-cached-property python311-PyYAML
# systemd (some tests list services using systemctl)
RUN zypper install -y systemd
