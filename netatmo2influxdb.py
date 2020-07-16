#!/usr/bin/env python

import logging
import os
import sys
import time

from influxdb import InfluxDBClient
from pyatmo.auth import ClientAuth
from pyatmo.weather_station import WeatherStationData
from urllib.error import HTTPError

def get_points(module):
    points = []

    if 'battery_vp' in module:
        points.append({
            'measurement': 'battery',
            'tags': {
                'id': module['_id'],
                'label': module['module_name'],
                'station': module['main_device'],
            },
            'fields': {
                'value': module['battery_vp'],
            }
        })

    if 'rf_status' in module:
        points.append({
            'measurement': 'rf_status',
            'tags': {
                'id': module['_id'],
                'label': module['module_name'],
                'station': module['main_device'],
            },
            'fields': {
                'value': module['rf_status'],
            }
        })

    if 'wifi_status' in module:
        points.append({
            'measurement': 'wifi_status',
            'tags': {
                'id': module['_id'],
                'label': module['station_name'],
            },
            'fields': {
                'value': module['wifi_status'],
            }
        })

    if 'dashboard_data' in module:
        for data_type in module['data_type']:
            points.append({
                'measurement': data_type.lower(),
                'tags': {
                    'id': module['_id'],
                    'label': module['module_name'],
                    'station': module['main_device'] if 'main_device' in module else module['_id'],
                },
                'time': module['dashboard_data']['time_utc'] * 1000000000, # need time in nano seconds
                'fields': {
                    'value': module['dashboard_data'][data_type] * 1.0,
                }
            })

    return points

def update(auth):
    try:
        weather = WeatherStationData(auth)
    except Exception as e:
        logging.warning('Unable to fetch weather data')
        logging.exception(e)
        return False

    points = []

    for station_id, station in weather.stations.items():
        logging.debug('Fetching points from station {} ({})...'.format(station['station_name'], station_id))

        station_points = get_points(station)

        if len(station_points):
            points.extend(station_points)
            logging.info('{} point(s) found from station {} ({}).'.format(
                len(station_points),
                station['station_name'],
                station_id)
            )

        for module in station['modules']:
            logging.debug('Fetching points from module {}:{} ({})...'.format(
                station['station_name'],
                module['module_name'],
                module['_id'],
            ))

            module_points = get_points(module)

            if len(module_points):
                points.extend(module_points)
                logging.info('{} point(s) found from module {}:{} ({}).'.format(
                    len(module_points),
                    station['station_name'],
                    module['module_name'],
                    module['_id'],
                ))

    if len(points):
        logging.debug('Writing {} point(s) to InfluxDB...'.format(
            len(points)
        ))

        try:
            client = InfluxDBClient(
                host=os.getenv('INFLUXDB_HOST'),
                port=os.getenv('INFLUXDB_PORT'),
                username=os.getenv('INFLUXDB_USER'),
                password=os.getenv('INFLUXDB_PASS'),
                database=os.getenv('INFLUXDB_BASE'),
                timeout=os.getenv('INFLUXDB_TIMEOUT', 10),
            )
            client.write_points(points)

            logging.info('Written {} point(s) to InfluxDB.'.format(
                len(points)
            ))
        except Exception as e:
            logging.error('Unable to write {} point(s) to InfluxDB'.format(
                len(points),
            ))
            logging.exception(e)
            return False

    return True

def usage():
    print('You need to define following environment variables:')
    print(' - NETATMO_CLIENT_ID')
    print(' - NETATMO_CLIENT_SECRET')
    print(' - NETATMO_USERNAME')
    print(' - NETATMO_PASSWORD')
    print(' - INFLUXDB_HOST')
    print(' - INFLUXDB_PORT')
    print(' - INFLUXDB_USER')
    print(' - INFLUXDB_PASS')
    print(' - INFLUXDB_BASE')

def main():
    logging_level = int(os.getenv('LOG_LEVEL', logging.INFO))
    logging.basicConfig(level=logging_level, format='[%(asctime)s] (%(levelname)s) %(message)s')

    # Check environment variables
    for env_name in [
        'NETATMO_CLIENT_ID',
        'NETATMO_CLIENT_SECRET',
        'NETATMO_USERNAME',
        'NETATMO_PASSWORD',
        'INFLUXDB_HOST',
        'INFLUXDB_PORT',
        'INFLUXDB_USER',
        'INFLUXDB_PASS',
        'INFLUXDB_BASE',
    ]:
        if os.getenv(env_name) is None:
            usage()
            sys.exit(1)

    try:
        auth = ClientAuth(
            client_id=os.getenv('NETATMO_CLIENT_ID'),
            client_secret=os.getenv('NETATMO_CLIENT_SECRET'),
            username=os.getenv('NETATMO_USERNAME'),
            password=os.getenv('NETATMO_PASSWORD'),
            scope='read_station',
        )
    except HTTPError as e:
        logging.error('Unable to connect to Netatmo API')
        logging.exception(e)
        sys.exit(1)

    logging.info('Logged in to Netatmo API as {}'.format(os.getenv('NETATMO_USERNAME')))

    while True:
        if not update(auth):
            logging.warning('Error while updating data')
        time.sleep(os.getenv('LOOP_DELAY', 30))

if '__main__' == __name__:
    main()
