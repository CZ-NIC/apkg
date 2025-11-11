FROM registry.nic.cz/packaging/apkg/systemd/ubuntu-18.04
ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8

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
    python3-setuptools
# apkg deps
RUN apt-get install -y -qqq \
    python3-bs4 \
    python3-blessings \
    python3-cached-property \
    python3-click \
    python3-distro \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
# python deps not available\too old in distro
RUN pip3 install \
    build
# install stable apkg from PyPI
RUN python3 -m pip install apkg
RUN apkg --version
