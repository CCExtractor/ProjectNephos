FROM centos:centos6.9
#centos6.9

VOLUME /pack
WORKDIR /pack

# install python3
# https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-centos-7

RUN \
	yum -y update && \
	yum -y install yum-utils && \
	yum -y groupinstall development && \
	yum -y install https://centos6.iuscommunity.org/ius-release.rpm && \
	yum -y install python36u python36u-pip && \
	pip3.6 install virtualenv && \
	true

# install dev-requirements

ADD requirements-dev.txt requirements-dev.txt

RUN \
	virtualenv build/env/centos6 && \
	pip3.6 install -r requirements-dev.txt && \
	true


ENTRYPOINT scripts/dev/pack-in-env.sh --env centos6
