FROM registry.nic.cz/packaging/apkg/systemd/fedora-42

WORKDIR /root
CMD ["/bin/bash"]
# add pip/pipx bin dir to $PATH
ENV PATH="/root/.local/bin:$PATH"

# upgrade system to latest
RUN dnf upgrade -y

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
