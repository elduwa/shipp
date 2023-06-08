from typing import Iterable
from flask import current_app
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.write.retry import WritesRetry
from datetime import datetime
import reactivex as rx
from reactivex import operators as ops


class DNSQueryMeasurement:
    def __init__(self, timestamp: int, client: str, query_type: str, reply_type: int, domain: str, status: int):
        self.timestamp = timestamp
        self.client = client
        self.query_type = query_type
        self.reply_type = reply_type
        self.domain = domain
        self.status = status


class BatchingCallback(object):

    def success(self, conf, data: str):
        current_app.logger.info(f"Written batch: {conf}, data: {data}")

    def error(self, conf, data: str, exception: InfluxDBError):
        current_app.logger.error(
            f"Cannot write batch: {conf}, data: {data} due: {exception}")

    def retry(self, conf, data: str, exception: InfluxDBError):
        current_app.logger.warning(
            f"Retryable error occurs for batch: {conf}, data: {data} retry: {exception}")


class InfluxDBClientWrapper:

    def __init__(self):
        self.influx_bucket = current_app.config['INFLUXDB_BUCKET']
        self._client = self.__create_influxdb_client()

    def __create_influxdb_client(self) -> InfluxDBClient:
        INFLUXDB_URL = current_app.config['INFLUXDB_URL']
        INFLUXDB_AUTH_TOKEN = current_app.config['INFLUXDB_AUTH_TOKEN']
        INFLUXDB_ORG = current_app.config['INFLUXDB_ORG']
        retries = WritesRetry(total=3, retry_interval=1, exponential_base=2)
        return InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_AUTH_TOKEN, org=INFLUXDB_ORG, retries=retries)

    def write_measurement(self, measurement: str, point):
        try:
            write_api = self._client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket=self.influx_bucket, record=point)
        except InfluxDBError as e:
            if e.response.status == 401:
                raise Exception(
                    f"Insufficient write permissions to '{self.influx_bucket}'.") from e
            raise e
        except Exception as e:
            current_app.logger.error(f"Error writing to InfluxDB: {e}")

    def write_batch(self, measurement: str, points):
        callback = BatchingCallback()
        with self._client.write_api(write_options=SYNCHRONOUS, success_callback=callback.success,
                                    error_callback=callback.error,
                                    retry_callback=callback.retry) as write_api:

            """
            Prepare batches from generator
            """
            batches = rx \
                .from_iterable(self.generate_datapoints(points)) \
                .pipe(ops.buffer_with_count(500)) \


            def write_batch_sync(batch):
                """
                Synchronous write
                """
                current_app.logger.info(f'Writing batch... {len(batch)}')
                write_api.write(bucket=self.influx_bucket, record=batch)

            """
            Write batches
            """
            batches.subscribe(on_next=lambda batch: write_batch_sync(batch),
                              on_error=lambda ex: print(
                                  f'Unexpected error: {ex}'),
                              on_completed=lambda: print('Write complete!'))

    def store_dns_query_measurements(self, measurements: Iterable[DNSQueryMeasurement]):
        for measurement in measurements:
            self.save_dns_query_measurement(measurement)

    def store_dns_query_measurements_batch(self, measurements: Iterable[DNSQueryMeasurement]):
        self.write_batch("dns_queries", measurements)

    def save_dns_query_measurement(self, measurement: DNSQueryMeasurement):
        point = Point("dns_queries").tag("client", measurement.client) \
            .tag("query_type", measurement.query_type) \
            .tag("reply_type", measurement.reply_type) \
            .field("queried_domain", measurement.domain) \
            .field("status", measurement.status) \
            .time(measurement.timestamp * 1000000000)
     #   current_app.logger.info(f"Writing measurement to InfluxDB: {point}")
        self.write_measurement("dns_queries", point)

    def generate_datapoints(self, measurements: Iterable[DNSQueryMeasurement]):
        for measurement in measurements:
            point = Point("dns_queries").tag("client", measurement.client) \
                .tag("query_type", measurement.query_type) \
                .tag("reply_type", measurement.reply_type) \
                .field("queried_domain", measurement.domain) \
                .field("status", measurement.status) \
                .time(time=datetime.fromtimestamp(measurement.timestamp), write_precision=WritePrecision.S)
            yield point

    def get_latest_timestamp(self, measurement: str) -> int:
        query = f'from(bucket: "{self.influx_bucket}") |> range(start: -1) |> last()'
        query_api = self._client.query_api()
        result = query_api.query(query)
        if len(result) > 0:
            latest_timestamp = result[0].records[0].get_time()
            return int(latest_timestamp.timestamp())
        else:
            return -1
