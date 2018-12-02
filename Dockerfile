
FROM geographica/gdal2:latest

MAINTAINER Min Feng
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y awscli cython3 python3-psycopg2 python3-boto python3-pandas python3-setuptools

ADD . /opt

ENV G_INI=/opt/ini
RUN cd /opt && python3 setup.py install

