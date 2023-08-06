import time
import pytz
import datetime

TO_MINUTE_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M'
TO_SECOND_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_timestamp():
    return time.time()


def timestamp_to_time(format, timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime(format)


def time_to_timestamp(format, input_time):
    date_time_obj = datetime.datetime.strptime(input_time, format)
    return date_time_obj.timestamp()


def convert_timezone(from_tz, to_tz, time_format, time_str):
    temp_time = datetime.datetime.strptime(time_str, time_format)
    from_timezone = pytz.timezone(from_tz)
    from_time = from_timezone.localize(temp_time, is_dst=None)
    assert from_time.tzinfo is not None
    assert from_time.tzinfo.utcoffset(from_time) is not None
    pst_time = from_time.astimezone(pytz.timezone(to_tz))
    return pst_time.strftime(time_format)

