#!/usr/bin/env python

import unittest
from pykeg.core import keg_sizes


class KegSizesTest(unittest.TestCase):
    def test_match(self):
        match = keg_sizes.find_closest_keg_size
        self.assertEqual('other', match(100.0))
        self.assertEqual('other', match(100000000.0))
        self.assertEqual('sixth', match(19570.6))
        self.assertEqual('sixth', match(19470.6))
        self.assertEqual('other', match(19460.6))

if __name__ == '__main__':
    unittest.main()
