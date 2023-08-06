import unittest
from BeautifulReport import BeautifulReport

if __name__ == "__main__":
    discover = unittest.defaultTestLoader.discover('.', pattern='*_test.py')
    print("Total Number Of Test Cases:", discover.countTestCases())
    result = BeautifulReport(discover)
    result.report(filename='test_report', report_dir="./target", description='Test Report', log_path=None)
