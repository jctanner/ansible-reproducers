FROM fedora:rawhide
MAINTAINER http://fedoraproject.org/wiki/Cloud

ENV container docker

RUN dnf -y update && dnf clean all

RUN dnf -y install systemd && dnf clean all && \
(cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;

RUN dnf -y install openssh openssh-server passwd sudo
RUN systemctl enable sshd
COPY testuser.sudo /etc/sudoers.d/testuser

RUN echo 'redhat1234' | passwd root --stdin
RUN mkdir -p /root/.ssh
COPY authorized_keys /root/.ssh/authorized_keys
RUN chown -R root:root /root
RUN chmod -R 700 /root/.ssh

RUN useradd testuser
RUN echo 'redhat1234' | passwd testuser --stdin
RUN mkdir -p /home/testuser/.ssh
COPY authorized_keys /home/testuser/.ssh/authorized_keys
RUN chown -R testuser:testuser /home/testuser
RUN chmod -R 700 /home/testuser/.ssh

RUN dnf -y install which procps-ng ntp
RUN dnf -y install python2

VOLUME [ "/sys/fs/cgroup", "/tmp", "/run" ]
CMD ["/usr/sbin/init"]
