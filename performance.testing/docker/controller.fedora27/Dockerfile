FROM fedora:27

RUN dnf clean all
RUN dnf -y install time
RUN dnf -y install ansible
RUN rpm -e --nodeps ansible
RUN dnf -y install python2-pip
RUN dnf -y install git
#RUN pip install ansible==2.5.0
