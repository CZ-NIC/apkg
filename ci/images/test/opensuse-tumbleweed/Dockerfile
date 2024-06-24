# SPDX-License-Identifier: GPL-3.0-or-later

FROM opensuse/tumbleweed

WORKDIR /root
CMD ["/bin/bash"]

# upgrade to latest
RUN zypper dup -y
# packaging deps
RUN zypper install -y curl git rpm-build python3-pip
# basic deps
RUN zypper install -y python3-beautifulsoup4 python3-setuptools python3-Jinja2 python3-click python3-distro python3-blessed python3-requests python3-toml python3-cached-property
# testing deps
RUN zypper install -y python3-pytest python3-pytest-sugar
# systemd (some tests list services using systemctl)
RUN zypper install -y systemd

# workaround PEP668 breaking pip installs
RUN mkdir -p /root/.config/pip && printf '[global]\nbreak-system-packages = true\n\n' >> /root/.config/pip/pip.conf
