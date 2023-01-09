FROM almalinux:9

ARG ARCH=amd64

RUN dnf update -y
RUN dnf install -y \
	systemd \
	git \
	git-lfs \
	man-db \
	https://gitlab-runner-downloads.s3.amazonaws.com/latest/rpm/gitlab-runner_${ARCH}.rpm

# autologin as root on console
RUN mkdir -p /etc/systemd/system/console-getty.service.d
COPY console-getty.conf /etc/systemd/system/console-getty.service.d/override.conf

CMD ["/sbin/init"]
