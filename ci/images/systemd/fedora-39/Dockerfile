FROM fedora:39

ARG ARCH=amd64

RUN dnf update -y
RUN dnf install -y \
	systemd \
	git \
	git-lfs \
	https://gitlab-runner-downloads.s3.amazonaws.com/latest/rpm/gitlab-runner_${ARCH}.rpm

# autologin as root on console
RUN mkdir -p /etc/systemd/system/console-getty.service.d
COPY console-getty.conf /etc/systemd/system/console-getty.service.d/override.conf

# disable systemd-oomd
RUN systemctl disable systemd-oomd.socket systemd-oomd.service && \
	systemctl mask systemd-oomd.service
# disable systemd-resolved
RUN systemctl disable systemd-resolved.service

# allow installation of man pages
RUN sed -i 's/tsflags=nodocs//' /etc/dnf/dnf.conf

CMD ["/sbin/init"]
