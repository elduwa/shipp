import time
import random
import pandas as pd
from flask import current_app
from app.service_integration_api import PiholeConsumer
from app.models.influxdb_model import DNSQueryMeasurement, InfluxDBClientWrapper
from app.models.database_model import DeviceConfig, Device
from app.extensions import db
from datetime import datetime
from requests.exceptions import ConnectionError


def fetch_query_data_job():
    current_app.logger.info('starting job...')
    # Load latest record from influxdb and find timestamp
    influxdb_client = InfluxDBClientWrapper()
    latest_timestamp = influxdb_client.get_latest_timestamp("dns_queries")
    from_timestamp = datetime.now().timestamp() - current_app.config['SCHEDULER_TIMEINTERVAL'] \
        if latest_timestamp == -1 else latest_timestamp
    until_timestamp = int(datetime.now().timestamp())
    # Query pihole for new data (load auth token from rel db --> for now use .env)
    # TODO: load AUTH_TOKEN from User
    auth_token = current_app.config['PIHOLE_AUTH_TOKEN']
    pihole_domain = current_app.config['PIHOLE_DOMAIN']
    pihole_consumer = PiholeConsumer(pihole_domain, auth_token)

    query_data = pihole_consumer.get_all_queries_ts(
        from_timestamp, until_timestamp)['data']

    # Get all active ips from db
    active_ips = db.session.execute(
        db.select(DeviceConfig.ip_address).where(DeviceConfig.valid_to == None)).scalars().all()  # noqa: E711
    active_ip_set = set(active_ips)

    dns_query_measurements = []

    # Process data
    for datapoint in query_data:
        client = datapoint[3]
        # Filter out data from inactive/unregistered clients
        if client not in active_ip_set:
            continue
        timestamp = int(datapoint[0])
        query_type = datapoint[1]
        domain = datapoint[2]
        status = datapoint[4]
        reply_type = datapoint[6]
        measurement = DNSQueryMeasurement(
            timestamp, client, query_type, reply_type, domain, status)
        dns_query_measurements.append(measurement)

    current_app.logger.info(
        f"Writing {len(dns_query_measurements)} new datapoints to influxdb...")
    # Write new data to influxdb
    influxdb_client.store_dns_query_measurements_batch(
        dns_query_measurements)


def weekly_summary():
    return pihole_queries_df(int(datetime.now().timestamp()) - 604800,
                             int(datetime.now().timestamp()))


def last_24h_summary():
    return pihole_queries_df(int(datetime.now().timestamp()) - 86400,
                             int(datetime.now().timestamp()))


def pihole_queries_df(from_timestamp: int, until_timestamp: int):
    pihole_domain = current_app.config['PIHOLE_DOMAIN']
    auth_token = current_app.config['PIHOLE_AUTH_TOKEN']
    pihole_consumer = PiholeConsumer(pihole_domain, auth_token)

    success = False
    max_retries = 2
    retries = 0
    error: ConnectionError | None = None
    while not success and retries < max_retries:
        try:
            query_data = pihole_consumer.get_all_queries_ts(
                from_timestamp, until_timestamp)['data']
            success = True
        except ConnectionError as e:
            current_app.logger.error(f"Cannot connect to pihole, retry in 5 s. Error: {e}")
            error = e
            retries += 1
            time.sleep(5)
            continue

    if not success:
        raise ConnectionError(error)

    # Get all active ips from db
    active_ips = db.session.execute(
        db.select(DeviceConfig.ip_address).where(DeviceConfig.valid_to == None)).scalars().all()  # noqa: E711
    active_ip_set = set(active_ips)

    dataset = []

    for datapoint in query_data:
        client = datapoint[3]
        # Filter out data from inactive/unregistered clients
        if client not in active_ip_set:
            continue
        timestamp = int(datapoint[0])
        query_type = datapoint[1]
        domain = datapoint[2]
        status = datapoint[4]
        reply_type = datapoint[6]
        dataset.append([timestamp, client, query_type, domain, status, reply_type])

    column_names = ['timestamp_sec', 'client', 'query_type', 'domain', 'status', 'reply_type']

    df = pd.DataFrame(dataset, columns=column_names)
    df['timestamp'] = pd.to_datetime(df['timestamp_sec'], unit='s').dt.tz_localize('Europe/Zurich')

    ip_name_map = get_ip_name_mapping()
    df['client_name'] = df['client'].map(lambda x: ip_name_map[x] if x in ip_name_map else x)

    return df


def dummy_weekly_summary():
    current_timestamp = int(datetime.now().timestamp())
    from_timestamp = current_timestamp - 604800
    until_timestamp = current_timestamp

    active_ips = ['192.168.1.100', '192.168.1.101', '192.168.1.102']
    query_types = ['A', 'AAAA', 'CNAME', 'MX', 'PTR']
    statuses = ['OK', 'Blocked']
    reply_types = ['NODATA', 'IP', 'CNAME']

    dataset = []

    for _ in range(1000):
        client = random.choice(active_ips)
        timestamp = random.randint(from_timestamp, until_timestamp)
        query_type = random.choice(query_types)
        domain = 'example.com'
        status = random.choice(statuses)
        reply_type = random.choice(reply_types)

        dataset.append([timestamp, client, query_type, domain, status, reply_type])

    column_names = ['timestamp_sec', 'client', 'query_type', 'domain', 'status', 'reply_type']
    df = pd.DataFrame(dataset, columns=column_names)
    df['timestamp'] = pd.to_datetime(df['timestamp_sec'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Europe/Zurich')

    return df


def get_ip_name_mapping():
    devices = db.session.execute(db.select(Device)).scalars().all()
    ip_name_map = dict()
    for device in devices:
        device_config = device.get_current_config()
        if device_config is not None:
            ip_name_map[device_config.ip_address] = device.device_name
        else:
            continue
    return ip_name_map
