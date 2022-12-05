FROM opensuse/leap:15.2

ARG ARCH=amd64

RUN zypper update -y
RUN zypper install -y \
	systemd \
	systemd-sysvinit \
	git \
	git-lfs \
	curl \
	tar

RUN curl -LJO "https://gitlab-runner-downloads.s3.amazonaws.com/latest/rpm/gitlab-runner_${ARCH}.rpm" \
	&& rpm -i "gitlab-runner_${ARCH}.rpm" \
	&& rm "gitlab-runner_${ARCH}.rpm"

# autologin as root on console
RUN mkdir -p /etc/systemd/system/console-getty.service.d
COPY console-getty.conf /etc/systemd/system/console-getty.service.d/override.conf

CMD ["/sbin/init"]
