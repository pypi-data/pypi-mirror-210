from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging


class Scheduler:

    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.start()
        logging.info("scheduler started!")

    def stop(self):
        self.scheduler.remove_all_jobs()
        self.scheduler.shutdown()
        logging.info("scheduler stopped!")

    def add_periodical_job(self, job_id, func, interval_seconds, parameters=None):
        self.scheduler.add_job(func, 'interval', kwargs=parameters, seconds=interval_seconds, id=job_id)
        logging.info("added periodical job {} with interval {}s into scheduler".format(job_id, interval_seconds))

    def remove_job(self, job_id):
        self.scheduler.remove_job(job_id=job_id)
        logging.info("removed periodical job {} from scheduler".format(job_id))


if __name__ == "__main__":
    def test():
        print('test')
        # time.sleep(3)
    scheduler = Scheduler()
    scheduler.start()
    scheduler.add_periodical_job('test', test, 1)
    time.sleep(5)
    # scheduler.remove_job('test')
    # time.sleep(3)
    scheduler.stop()
    time.sleep(2)
