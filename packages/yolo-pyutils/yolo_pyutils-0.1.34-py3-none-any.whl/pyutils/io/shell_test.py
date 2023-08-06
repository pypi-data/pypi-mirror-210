import unittest
from pyutils.io.shell import run
import codecs


class TestShell(unittest.TestCase):

    def test_execute_cmd(self):
        stdout, stderr = run("echo xxx")
        self.assertEqual(stdout, "xxx")
        self.assertEqual(stderr, "")
        try:
            run("fail 2s")
            self.fail("should fail")
        except Exception as e:
            self.assertTrue(str(e).find('No such file or directory') != -1)
        try:
            run("sleep 10s", 1)
            self.fail("should fail")
        except Exception as e:
            self.assertTrue(str(e).find('timed out after 1 seconds') != -1)


if __name__ == "__main__":
    unittest.main()
