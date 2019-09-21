
FROM geographica/gdal2:latest
# FROM thinkwhere/gdal-python:3.7-ubuntu
# FROM osgeo/gdal:ubuntu-small-latest

LABEL creator Min Feng
ENV DEBIAN_FRONTEND noninteractive

RUN rm /usr/bin/python

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN apt-get update && apt-get install -y awscli python3-psycopg2 python3-pip
RUN apt remove -y python3-numpy

# RUN apt-get update && apt-get install -y awscli cython3 python3-psycopg2 python3-boto3 python3-pandas python3-setuptools python3-pip
# RUN apt remove -y python3-numpy
RUN pip3 install watchtower numpy pandas cython boto3 setuptools

WORKDIR /opt

ENV G_INI=/opt/ini
ENV G_LOG=/opt/log
ENV G_TMP=/opt/tmp

ADD . /opt/lib
RUN cd /opt/lib && python3 setup.py install
RUN rm -rf /opt/lib

ENTRYPOINT []
