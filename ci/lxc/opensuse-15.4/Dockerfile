FROM registry.nic.cz/labs/lxc-gitlab-runner/opensuse-15.4
ENV LC_ALL=C.UTF-8

WORKDIR /root
CMD ["/bin/bash"]


# packaging deps
RUN zypper install -y curl git rpm-build python3-pip
# basic deps
RUN zypper install -y python3-beautifulsoup4 python3-setuptools python3-Jinja2 python3-click python3-distro python3-blessings python3-requests python3-toml python3-cached-property
# systemd
RUN zypper install -y systemd
# install stable apkg from PyPI
RUN python3 -m pip install apkg
RUN apkg --version
