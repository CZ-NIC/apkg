# SPDX-License-Identifier: GPL-3.0-or-later

FROM archlinux

WORKDIR /root
CMD ["/bin/bash"]
# add pip/pipx bin dir to $PATH
ENV PATH="/root/.local/bin:$PATH"

# upgrade system to latest
RUN pacman -Syu --noconfirm

# packaging deps
RUN pacman -Sy --noconfirm \
    base-devel \
    git \
    man-db \
    python-setuptools \
    python-pip \
    python-pipx
# basic deps
RUN pacman -Sy --noconfirm \
    python-beautifulsoup4 \
    python-blessed \
    python-click \
    python-distro \
    python-jinja \
    python-packaging \
    python-requests \
    python-toml
# testing deps
RUN pacman -Sy --noconfirm \
    python-pytest \
    python-pytest-sugar \
    sudo

# enable man pages
RUN sed -i '/^NoExtract/d' /etc/pacman.conf
# makepkg can't run as root :(
RUN useradd -m test
RUN echo 'test    ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/test_user
# add pip/pipx bin dir to $PATH for all users (needs interactive shell)
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> /etc/profile.d/pipbin.sh

# workaround PEP668 breaking pip installs
RUN mkdir -p /root/.config/pip && printf '[global]\nbreak-system-packages = true\n\n' >> /root/.config/pip/pip.conf
RUN mkdir -p /home/test/.config/pip && printf '[global]\nbreak-system-packages = true\n\n' >> /home/test/.config/pip/pip.conf && chown -R test /home/test/.config
