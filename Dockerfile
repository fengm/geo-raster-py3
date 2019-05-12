
FROM geographica/gdal2:latest

LABEL creator Min Feng
ENV DEBIAN_FRONTEND noninteractive

RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get update && apt-get install -y awscli cython3 python3-psycopg2 python3-boto python3-pandas python3-setuptools python3-pip
RUN pip3 install watchtower

WORKDIR /opt

ENV G_INI=/opt/ini
ENV G_LOG=/opt/log
ENV G_TMP=/opt/tmp

ADD . /opt/lib
RUN cd /opt/lib && python3 setup.py install
RUN rm -rf /opt/lib

ENTRYPOINT []
