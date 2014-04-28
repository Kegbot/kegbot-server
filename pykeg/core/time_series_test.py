#!/usr/bin/env python

import unittest
from pykeg.core import time_series


class TimeSeriesTestCase(unittest.TestCase):
    def testTimeSeries(self):
        s = "  0:12 45:6789  "
        expected = [(0, 12), (45, 6789)]
        self.assertEqual(expected, time_series.from_string(s))

        self.assertEqual(s.strip(), time_series.to_string(expected))

if __name__ == '__main__':
    unittest.main()
