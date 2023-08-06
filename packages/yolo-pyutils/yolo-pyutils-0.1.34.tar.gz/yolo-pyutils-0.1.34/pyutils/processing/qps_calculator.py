import time
from collections import OrderedDict
from pyutils.structures.time import TO_MINUTE_DATE_TIME_FORMAT


class QPSCalculator:

    def __init__(self):
        self.__qps_buckets_in_minutes = OrderedDict()

    def add(self, timestamp, num=1):
        struct_time = time.localtime(timestamp)
        minute_str = time.strftime(TO_MINUTE_DATE_TIME_FORMAT, struct_time)
        qps_buckets = self.__qps_buckets_in_minutes.get(minute_str)
        if qps_buckets is None:
            qps_buckets = [0] * 60
            self.__qps_buckets_in_minutes[minute_str] = qps_buckets
        sec_index = struct_time.tm_sec if struct_time.tm_sec < 60 else 59
        qps_buckets[sec_index] += num

    def get_qps_in_minutes(self):
        rst = OrderedDict()
        for minute_str, qps_buckets in self.__qps_buckets_in_minutes.items():
            rst[minute_str] = float(sum(qps_buckets)) / len(qps_buckets)
        return rst

    def get_qps_buckets_in_minutes(self):
        return self.__qps_buckets_in_minutes
