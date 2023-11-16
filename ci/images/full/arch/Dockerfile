FROM registry.nic.cz/packaging/apkg/systemd/arch

WORKDIR /root
CMD ["/bin/bash"]
# add pip/pipx bin dir to $PATH
ENV PATH="~/.local/bin:$PATH"

# upgrade system to latest
RUN pacman -Syu --noconfirm

# packaging deps
RUN pacman -Sy --noconfirm \
    base-devel \
    git \
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
# Arch being special deps
RUN pacman -Sy --noconfirm \
    sudo

# enable man pages
RUN sed -i '/^NoExtract/d' /etc/pacman.conf
# makepkg can't run as root :(
RUN useradd -m test
RUN echo 'test    ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/test_user

# install stable apkg from PyPI
RUN pip install apkg --break-system-packages
RUN apkg --version
