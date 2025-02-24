FROM almalinux:10-kitten

ARG ARCH=amd64

RUN dnf update -y
RUN dnf install -y \
	systemd \
	git \
	git-lfs \
	man-db

# autologin as root on console
RUN mkdir -p /etc/systemd/system/console-getty.service.d
COPY console-getty.conf /etc/systemd/system/console-getty.service.d/override.conf

CMD ["/sbin/init"]
