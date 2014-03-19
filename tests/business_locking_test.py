from lib import data

import random
import unittest

class TestBusinessLocking(unittest.TestCase):

    def setUp(self):
        pass

    def test_locking(self):
        s = data.Storage()
        key = "testing"
        self.assertTrue(s.get_lock(key))
        self.assertFalse(s.get_lock(key))
        s.release_lock(key)
        self.assertTrue(s.get_lock(key))
        self.assertFalse(s.get_lock(key))
        s.release_lock(key)

if __name__ == '__main__':
    unittest.main()
