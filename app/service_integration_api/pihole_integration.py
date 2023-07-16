import requests
from datetime import datetime


class Query:

    def __init__(self, base_url: str):
        self._base_url = base_url
        self._query_params = {}

    def add_param(self, key: str, value: str):
        self._query_params[key] = value

    def send_request(self) -> dict:
        response = requests.get(self._base_url, params=self._query_params)
        return response.json()


class QueryBuilder:

    def __init__(self, domain):
        self.pihole_api_base_url = "".join(["http://", domain, "/admin/api.php"])
        self.reset()

    def reset(self):
        self._query = Query(self.pihole_api_base_url)

    @property
    def query(self) -> Query:
        query = self._query
        self.reset()
        return query

    def add_auth_token(self, auth_token: str):
        self._query.add_param("auth", auth_token)

    def type_all_queries(self):
        self._query.add_param("getAllQueries", "1")

    def type_summary_raw(self):
        self._query.add_param("summaryRaw", "1")

    def type_top_clients(self, num_clients: int):
        self._query.add_param("topClients", str(num_clients))

    def type_over_time_data(self, days: int):
        self._query.add_param("overTimeData", str(days))

    def add_from(self, timestamp: int):
        self._query.add_param("from", str(timestamp))

    def add_until(self, timestamp: int):
        self._query.add_param("until", str(timestamp))


class PiholeConsumer:

    def __init__(self, pihole_domain, auth_token: str):
        self._pihole_domain = pihole_domain
        self._auth_token = auth_token

    def get_all_queries_ts(self, from_timestamp: int, until_timestamp: int) -> dict:
        builder = QueryBuilder(self._pihole_domain)
        builder.add_auth_token(self._auth_token)
        builder.type_all_queries()
        builder.add_from(from_timestamp)
        builder.add_until(until_timestamp)
        response = builder.query.send_request()
        return response

    def get_topclients(self, num_clients: int) -> dict:
        builder = QueryBuilder(self._pihole_domain)
        builder.add_auth_token(self._auth_token)
        builder.type_top_clients(num_clients)
        response = builder.query.send_request()
        return response

    def datetime_str_to_timestamp(self, datetime_str):
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S %z")

            # Convert the datetime object to a Unix timestamp
            timestamp = dt.timestamp()
            return int(timestamp)

        except ValueError:
            raise ValueError(
                "Invalid datetime format. Expected format: '%Y-%m-%d %H:%M:%S %z'")
