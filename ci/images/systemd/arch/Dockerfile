FROM archlinux

ARG ARCH=amd64

RUN pacman -Syu --noconfirm
RUN pacman -Sy --noconfirm \
	systemd \
	git \
	git-lfs \
	man-db \
    gitlab-runner

# set timezone
RUN ln -s /usr/share/zoneinfo/UTC /etc/localtime

# autologin as root on console
RUN mkdir -p /etc/systemd/system/console-getty.service.d
COPY console-getty.conf /etc/systemd/system/console-getty.service.d/override.conf

CMD ["/sbin/init"]
