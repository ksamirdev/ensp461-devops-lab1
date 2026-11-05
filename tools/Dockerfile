# Ubuntu 24.04 lab host with systemd, so Jenkins and the app run as real services
FROM public.ecr.aws/docker/library/ubuntu:24.04
RUN apt-get update -qq && apt-get install -y -qq systemd systemd-sysv sudo dbus iproute2 ca-certificates \
 && useradd -m -s /bin/bash samir && echo 'samir ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/samir
STOPSIGNAL SIGRTMIN+3
CMD ["/sbin/init"]
