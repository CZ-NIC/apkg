FROM registry.nic.cz/packaging/apkg/systemd/debian-13
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
    python3-all \
    python3-pip \
    python3-setuptools \
    pipx
# apkg deps
RUN apt-get install -y -qqq \
    python3-bs4 \
    python3-blessed \
    python3-build \
    python3-click \
    python3-distro \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
# install stable apkg from PyPI
RUN python3 -m pip install --break-system-packages apkg
RUN apkg --version
