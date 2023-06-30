from app.service_integration_api import PiholeConsumer
import requests
from tests import utils


def test_get_all_queries(mocker, app):
    pihole_consumer = PiholeConsumer("test-domain", "test_auth_token")

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"key": "value"}

    mocker.patch('requests.get', return_value=mock_response)

    from_datetime, until_datetime = utils.generate_random_from_until_datetimes()
    from_str = utils.datetime_to_string(from_datetime)
    until_str = utils.datetime_to_string(until_datetime)

    result = pihole_consumer.get_all_queries_dt(
        from_str, until_str)

    requests.get.assert_called_once_with(
        "http://test-domain/admin/api.php", params={"auth": "test_auth_token",
                                                    "getAllQueries": "1",
                                                    "from": str(utils.datetime_to_unix_timestamp(from_datetime)),
                                                    "until": str(utils.datetime_to_unix_timestamp(until_datetime))})

    assert result == {"key": "value"}
