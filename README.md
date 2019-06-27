# netatmo2influxdb
Import Netatmo Weather to InfluxDB

## Run it with docker

```
docker run \
    -d \
    -e NETATMO_CLIENT_ID='<your_netatmo_client_id>' \
    -e NETATMO_CLIENT_SECRET='<your_netatmo_client_secret>' \
    -e NETATMO_USERNAME='<your_netatmo_username>' \
    -e NETATMO_PASSWORD='<your_netatmo_password>' \
    -e INFLUXDB_HOST='<your_influxdb_host>' \
    -e INFLUXDB_PORT='<your_influxdb_port>' \
    -e INFLUXDB_USER='<your_influxdb_user>' \
    -e INFLUXDB_PASS='<your_influxdb_pass>' \
    -e INFLUXDB_BASE='<your_influxdb_base>' \
    rclsilver/netatmo2influxdb-amd64:latest
```

## Run it with kubernetes

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: netatmo2influxdb
  labels:
    name: netatmo2influxdb
    app: netatmo2influxdb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: netatmo2influxdb
  template:
    metadata:
      name: netatmo2influxdb
      labels:
        app: netatmo2influxdb
        name: netatmo2influxdb
    spec:
      nodeSelector:
        kubernetes.io/arch: amd64
      restartPolicy: Always
      containers:
      - name: netatmo2influxdb
        image: rclsilver/netatmo2influxdb-amd64:v1.0.0
        imagePullPolicy: IfNotPresent
        env:
          - name: NETATMO_CLIENT_ID
            value: "<your_netatmo_client_id>"
          - name: NETATMO_CLIENT_SECRET
            value: "<your_netatmo_client_secret>"
          - name: NETATMO_USERNAME
            value: "<your_netatmo_username>"
          - name: NETATMO_PASSWORD
            value: "<your_netatmo_password>"
          - name: INFLUXDB_HOST
            value: "<your_influxdb_host>"
          - name: INFLUXDB_PORT
            value: "<your_influxdb_port>"
          - name: INFLUXDB_USER
            value: "<your_influxdb_user>"
          - name: INFLUXDB_PASS
            value: "<your_influxdb_pass>"
          - name: INFLUXDB_BASE
            value: "<your_influxdb_base>"
```
