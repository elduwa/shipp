from datetime import datetime, timedelta
import random
import pytz


def generate_random_from_until_datetimes():
    now = datetime.now()
    # Subtract 20 years from the current time
    max_start_time = now - timedelta(days=365 * 20)

    start_timestamp = random.randint(
        int(max_start_time.timestamp()), int(now.timestamp()))
    finish_timestamp = random.randint(start_timestamp, int(now.timestamp()))

    start_time = datetime.fromtimestamp(start_timestamp, tz=pytz.UTC)
    finish_time = datetime.fromtimestamp(finish_timestamp, tz=pytz.UTC)

    random_timezone = random.choice(pytz.all_timezones)
    start_time = start_time.astimezone(pytz.timezone(random_timezone))
    finish_time = finish_time.astimezone(pytz.timezone(random_timezone))

    return start_time, finish_time


def datetime_to_string(dt):
    return datetime.strftime(dt, "%Y-%m-%d %H:%M:%S %z")


def datetime_to_unix_timestamp(dt):
    return int(dt.timestamp())
