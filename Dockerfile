FROM amd64/python:3.7-alpine AS amd64
FROM arm32v7/python:3.7-alpine AS arm32v7

ENV VERSION 1.0.0

COPY netatmo2influxdb.py /usr/local/bin/netatmo2influxdb
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

CMD [ "/usr/local/bin/netatmo2influxdb" ]