# SPDX-License-Identifier: GPL-3.0-or-later

FROM centos:7
ENV LC_ALL=C.UTF-8

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
# testing deps
RUN pip3 install \
    pytest
