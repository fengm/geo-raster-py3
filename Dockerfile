
FROM geographica/gdal2:latest

LABEL creator Min Feng
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y awscli cython3 python3-psycopg2 python3-boto python3-pandas python3-setuptools

WORKDIR /opt

ADD . /opt/lib
RUN cd /opt/lib && python3 setup.py install
RUN rm -rf /opt/lib
