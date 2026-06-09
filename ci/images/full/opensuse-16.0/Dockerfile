FROM registry.nic.cz/packaging/apkg/systemd/opensuse-16.0
ENV LC_ALL=C.UTF-8
ENV PATH="~/.local/bin:${PATH}"

WORKDIR /root
CMD ["/bin/bash"]
SHELL ["/bin/bash", "-c"]

# packaging deps
RUN zypper --non-interactive install --force-resolution \
    curl \
    git \
    rpm-build \
    python3 \
    python3-pipx

# basic deps
RUN zypper --non-interactive install \
    python313-beautifulsoup4 \
    python313-setuptools \
    python313-Jinja2 \
    python313-click \
    python313-distro \
    python313-blessings \
    python313-requests \
    python313-toml

# systemd
RUN zypper --non-interactive install \
    systemd

# install stable apkg from PyPI
RUN echo 'PATH="~/.local/bin:${PATH}"' >> ~/.bashrc
RUN pipx install apkg

RUN apkg --version
