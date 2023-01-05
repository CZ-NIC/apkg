FROM registry.nic.cz/packaging/apkg/systemd/alma-9
ENV LC_ALL=C.UTF-8

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN dnf upgrade -y
# get dnf plugins
RUN dnf install -y dnf-plugins-core
# enable crb (PowerTools)
RUN dnf config-manager --set-enabled crb
# enable EPEL
RUN dnf install -y epel-release
# update repos
RUN dnf update -y

# packaging deps
RUN dnf install -y \
    git \
    rpm-build \
    python3-pip
# basic deps
RUN dnf install -y \
    python3-beautifulsoup4 \
    python3-cached-property \
    python3-click \
    python3-distro \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
# not available from distro packages
RUN pip3 install \
    blessings
# testing deps
RUN pip3 install \
    pytest \
    pytest-sugar
# install stable apkg from PyPI
RUN python3 -m pip install apkg
RUN apkg --version
