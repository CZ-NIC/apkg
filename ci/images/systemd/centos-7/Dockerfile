FROM centos:7

ARG ARCH=amd64

RUN yum update -y
RUN yum install -y \
	systemd \
	git \
	git-lfs \
	https://gitlab-runner-downloads.s3.amazonaws.com/latest/rpm/gitlab-runner_${ARCH}.rpm

# autologin as root on console
RUN mkdir -p /etc/systemd/system/console-getty.service.d
COPY console-getty.conf /etc/systemd/system/console-getty.service.d/override.conf

CMD ["/sbin/init"]
