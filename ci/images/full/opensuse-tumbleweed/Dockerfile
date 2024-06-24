FROM registry.nic.cz/packaging/apkg/systemd/opensuse-tumbleweed
ENV LC_ALL=C.UTF-8
ENV PATH="~/.local/bin:${PATH}"

WORKDIR /root
CMD ["/bin/bash"]
SHELL ["/bin/bash", "-c"]


# packaging deps
RUN zypper install -y --force-resolution curl git rpm-build python311-pipx
# basic deps
RUN zypper install -y python311-beautifulsoup4 python311-setuptools python311-Jinja2 python311-click python311-distro python311-blessed python311-requests python311-toml
# systemd
RUN zypper install -y systemd
# install stable apkg from PyPI
RUN echo 'PATH="~/.local/bin:${PATH}"' >> ~/.bashrc
RUN pipx install apkg
RUN apkg --version
