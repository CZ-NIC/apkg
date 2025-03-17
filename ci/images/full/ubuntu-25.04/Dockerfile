FROM registry.nic.cz/packaging/apkg/systemd/ubuntu-25.04
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root
CMD ["/bin/bash"]
# add pip/pipx bin dir to $PATH
ENV PATH="/root/.local/bin:$PATH"

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

# add pip/pipx bin dir to $PATH for all users (needs interactive shell)
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> /etc/profile.d/pipbin.sh

# install stable apkg from PyPI into pipx venv
RUN pipx install apkg
RUN apkg --version
