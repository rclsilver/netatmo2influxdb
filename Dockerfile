ARG ARCH

FROM ${ARCH}/python:3.7-alpine

ENV VERSION 1.1.0

COPY netatmo2influxdb.py /usr/local/bin/netatmo2influxdb
COPY requirements.txt /tmp/requirements.txt

RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

CMD [ "python3", "/usr/local/bin/netatmo2influxdb" ]
