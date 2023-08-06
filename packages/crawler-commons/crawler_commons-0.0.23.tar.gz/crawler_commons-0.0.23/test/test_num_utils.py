import unittest

import numpy as np

from crawlutils.num_utils import to_int, to_float


class TestNumUtils(unittest.TestCase):

    def test_to_int(self):
        self.assertEqual(to_int("+1,000"), 1000)
        self.assertEqual(to_int("1,000"), 1000)
        self.assertEqual(to_int("-1,000"), -1000)
        self.assertEqual(to_int("1,000.24"), 1000)
        self.assertEqual(to_int("-1,000.24"), -1000)
        self.assertTrue(np.isnan(to_int(np.nan)))
        self.assertTrue(np.isnan(to_int(" ")))
        self.assertTrue(np.isnan(to_int("-")))
        self.assertTrue(np.isnan(to_int(" - ")))

    def test_to_float(self):
        self.assertEqual(to_float("1,000"), 1000)
        self.assertEqual(to_float("-1,000"), -1000)
        self.assertEqual(to_float("1,000.24"), 1000.24)
        self.assertEqual(to_float("-1,000.24"), -1000.24)
        self.assertTrue(np.isnan(to_float(np.nan)))
        self.assertTrue(np.isnan(to_float(" ")))
        self.assertTrue(np.isnan(to_float("-")))
        self.assertTrue(np.isnan(to_float(" - ")))