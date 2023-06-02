from flask import current_app
from app.service_integration_api import PiholeConsumer
from app.extensions import scheduler
from app.models.influxdb_model import DNSQueryMeasurement, InfluxDBClientWrapper
from datetime import datetime

# with scheduler.app.app_context():
#   SCHEDULER_TIMEINTERVAL = current_app.config['SCHEDULER_TIMEINTERVAL']


# @scheduler.task('interval', id='fetch_query_data_job', seconds=20)
def fetch_query_data_job():
    # does it matter if i use scheduler.app or db.app??
    with scheduler.app.app_context():
        print('starting job...')
        current_app.logger.info('starting job...')
        # Load latest record from influxdb and find timestamp
        influxdb_client = InfluxDBClientWrapper()
        from_timestamp = influxdb_client.get_latest_timestamp(
            "dns_queries") - current_app.config['SCHEDULER_TIMEINTERVAL']
        until_timestamp = int(datetime.now().timestamp()
                              )
        # Query pihole for new data (load auth token from rel db --> for now use .env)
        auth_token = current_app.config['PIHOLE_AUTH_TOKEN']
        pihole_consumer = PiholeConsumer(auth_token)

        query_data = pihole_consumer.get_all_queries_ts(
            from_timestamp, until_timestamp)['data']

        dns_query_measurements = []

        # Process data
        for datapoint in query_data:
            timestamp = int(datapoint[0])
            current_app.logger.info(f"Timestamp: {timestamp}")
            query_type = datapoint[1]
            domain = datapoint[2]
            client = datapoint[3]
            status = datapoint[4]
            reply_type = datapoint[6]
            measurement = DNSQueryMeasurement(
                timestamp, client, query_type, reply_type, domain, status)
            dns_query_measurements.append(measurement)

        # Write new data to influxdb
        influxdb_client.store_dns_query_measurements_batch(
            dns_query_measurements)
