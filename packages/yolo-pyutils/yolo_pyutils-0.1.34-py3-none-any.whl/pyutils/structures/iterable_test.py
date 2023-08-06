import unittest
from pyutils.structures import iterable as iter_util


class TestIterable(unittest.TestCase):

    def test_has_negative(self):
        self.assertTrue(iter_util.has_negative((-1)))
        self.assertTrue(iter_util.has_negative((-5)))
        self.assertTrue(iter_util.has_negative((-1, 0)))
        self.assertTrue(iter_util.has_negative((0, -1)))
        self.assertTrue(iter_util.has_negative((-1, 1)))
        self.assertTrue(iter_util.has_negative((1, -1)))
        self.assertTrue(iter_util.has_negative((-3, 1)))
        self.assertTrue(iter_util.has_negative((-3, -1)))
        self.assertTrue(iter_util.has_negative((3, -3)))
        self.assertTrue(iter_util.has_negative((-1, 0, 1)))
        self.assertTrue(iter_util.has_negative((1, 2, -3)))

        self.assertFalse(iter_util.has_negative((0)))
        self.assertFalse(iter_util.has_negative((1)))
        self.assertFalse(iter_util.has_negative((6)))
        self.assertFalse(iter_util.has_negative((1, 0)))
        self.assertFalse(iter_util.has_negative((0, 1)))
        self.assertFalse(iter_util.has_negative((1, 1)))
        self.assertFalse(iter_util.has_negative((1, 2, 3)))
        self.assertFalse(iter_util.has_negative((1, 2, 3, 4, 5)))


if __name__ == '__main__':
    unittest.main()
