FROM ubuntu:25.04

ENV DEBIAN_FRONTEND=noninteractive
ARG ARCH=amd64

RUN apt-get update && apt-get install -y \
		systemd \
		init \
		dhcpcd5 \
		curl \
		git \
		git-lfs \
	&& rm -rf /var/lib/apt/lists/*

# autologin as root on console
RUN mkdir -p /etc/systemd/system/console-getty.service.d
COPY console-getty.conf /etc/systemd/system/console-getty.service.d/override.conf

# gitlab runner is needed for artifacts/cache
RUN curl -LJ -O "https://gitlab-runner-downloads.s3.amazonaws.com/latest/deb/gitlab-runner_${ARCH}.deb" \
	-O "https://gitlab-runner-downloads.s3.amazonaws.com/latest/deb/gitlab-runner-helper-images.deb" \
	&& dpkg -i "gitlab-runner_${ARCH}.deb" "gitlab-runner-helper-images.deb" \
	&& rm "gitlab-runner_${ARCH}.deb" "gitlab-runner-helper-images.deb"

RUN systemctl disable systemd-resolved.service

CMD ["/sbin/init"]
