FROM registry.nic.cz/packaging/apkg/systemd/centos-7

WORKDIR /root
CMD ["/bin/bash"]

# overcome locale issues
RUN yum install -y glibc-common
RUN localedef -i en_US -f UTF-8 C.UTF-8

# upgrade system to latest
RUN yum upgrade -y
# enable EPEL
RUN yum install -y epel-release

# packaging deps
RUN yum install -y \
    git \
    rpm-build \
    python3-setuptools \
    python3-pip
# basic deps
RUN pip3 install \
    beautifulsoup4 \
    blessings \
    cached-property \
    click \
    distro \
    jinja2 \
    packaging \
    requests \
    toml
# install stable apkg from PyPI
RUN python3 -m pip install apkg
RUN apkg --version
