import unittest
from pyutils.scheduling.scheduler import *


class TestScheduler(unittest.TestCase):

    def test_schedule(self):
        data1, data2 = list(), list()
        def append_data1():
            data1.append(1)
        def append_data2():
            data2.append(1)
        sched = Scheduler()
        sched.start()

        # add 2 periodical jobs
        sched.add_periodical_job("job1", append_data1, 0.01)
        sched.add_periodical_job("job2", append_data2, 0.01)

        # after 3 round, data controlled by jobs should be updated with 3 items
        time.sleep(0.033)
        self.assertEqual(3, len(data1))
        self.assertEqual(3, len(data2))

        # removed job1 should not continue counting
        sched.remove_job("job1")
        time.sleep(0.021)
        self.assertEqual(3, len(data1))
        self.assertEqual(5, len(data2))

        # all jobs are removed after scheduler stopped
        sched.stop()
        time.sleep(0.025)
        self.assertEqual(3, len(data1))
        self.assertEqual(5, len(data2))


if __name__ == '__main__':
    unittest.main()
