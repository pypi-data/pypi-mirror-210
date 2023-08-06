import datetime


class Timer:

    def __init__(self, start=True):
        if start:
            self.start_time = datetime.datetime.now()

    def start(self):
        self.start_time = datetime.datetime.now()

    def get_elapse_ms(self):
        elapse = datetime.datetime.now() - self.start_time
        return elapse.total_seconds() * 1000

    def get_elapse_s(self):
        elapse = datetime.datetime.now() - self.start_time
        return elapse.total_seconds()

