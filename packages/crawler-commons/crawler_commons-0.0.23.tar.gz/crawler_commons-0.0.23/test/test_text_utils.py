import unittest

import numpy as np

from crawlutils.text_utils import fmt_int, fmt_float


class TestTextUtils(unittest.TestCase):

    def test_fmt_int(self):
        self.assertEqual(fmt_int(1000, use_comma=True, default="-", postfix="원"), "1,000원")
        self.assertEqual(fmt_int(1000, use_comma=False, default="-", postfix="원"), "1000원")
        self.assertEqual(fmt_int(1000, use_comma=False, default="-", postfix=""), "1000")
        self.assertEqual(fmt_int(np.nan, use_comma=True, default="-", postfix="원"), "-")
        self.assertEqual(fmt_int("-", use_comma=True, default="-", postfix="원"), "-")
        self.assertEqual(fmt_int("-", use_comma=True, default="*", postfix="원"), "*")

    def test_fmt_float(self):
        self.assertEqual(fmt_float(1000, use_comma=True, precision=2, default="-", postfix="원"), "1,000.00원")
        self.assertEqual(fmt_float(1000, use_comma=False, precision=0, default="-", postfix="원"), "1000원")
        self.assertEqual(fmt_float(1000.12, use_comma=False, precision=1, default="-", postfix=""), "1000.1")
        self.assertEqual(fmt_float(np.nan, use_comma=True, default="-", postfix="원"), "-")
        self.assertEqual(fmt_float("-", use_comma=True, default="-", postfix="원"), "-")
        self.assertEqual(fmt_float("-", use_comma=True, default="*", postfix="원"), "*")