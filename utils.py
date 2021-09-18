from datetime import datetime, timedelta, timezone

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def timestamp_to_string(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(DATETIME_FORMAT)


def string_to_timestamp(datetime_string):
    date_time = datetime.strptime(datetime_string, DATETIME_FORMAT)
    return int(date_time.replace(tzinfo=timezone.utc).timestamp())


def get_seconds_till_timestamp(timestamp):
    return (timestamp - datetime.now()).total_seconds()


def get_timestamp_after_seconds(seconds):
    return datetime.now() + timedelta(seconds=seconds)



if __name__ == '__main__':
    # datetime_string = "2021-10-11 21:05:10"
    # timestamp = string_to_timestamp(datetime_string)
    # string = timestamp_to_string(timestamp)

    print(get_seconds_till_timestamp(get_timestamp_after_seconds(60)))