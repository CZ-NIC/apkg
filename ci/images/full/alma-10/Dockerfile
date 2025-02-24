FROM registry.nic.cz/packaging/apkg/systemd/alma-10
ENV LC_ALL=C.UTF-8

WORKDIR /root
CMD ["/bin/bash"]
# add pip/pipx bin dir to $PATH
ENV PATH="/root/.local/bin:$PATH"

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
    python3-pip \
    pipx

# add pip/pipx bin dir to $PATH for all users (needs interactive shell)
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> /etc/profile.d/pipbin.sh

# install stable apkg from PyPI into pipx venv
RUN pipx install apkg
RUN apkg --version
