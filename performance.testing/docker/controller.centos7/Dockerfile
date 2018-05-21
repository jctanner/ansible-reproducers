FROM centos:7.4.1708

RUN yum clean all && yum -y install epel-release
RUN yum -y install time
RUN yum -y install ansible
RUN rpm -e --nodeps ansible
RUN yum -y install python-pip
RUN yum -y install git
#RUN pip install ansible==2.5.0
