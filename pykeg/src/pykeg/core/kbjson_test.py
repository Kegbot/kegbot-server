#!/usr/bin/env python

"""Unittest for kbjson module"""

import datetime
import kbjson
import unittest

from pykeg.core import util

SAMPLE_INPUT = """
{
  "event": "my-event",
  "sub" : {
    "list" : [1,2,3]
  },
  "iso_time": "2010-06-11T23:01:01Z",
  "bad_time": "123-45"
}
"""

class JsonTestCase(unittest.TestCase):
  def setUp(self):
    pass

  def testTzSwap(self):
    import pytz
    PACIFIC = pytz.timezone('America/Los_Angeles')
    EASTERN = pytz.timezone('America/New_York')
    GMT = pytz.timezone('GMT')

    eastern_stamp = datetime.datetime(2010, 12, 30, 8)
    as_pacific = util.tzswap(eastern_stamp, EASTERN, PACIFIC)
    self.assertEqual(as_pacific, datetime.datetime(2010, 12, 30, 5))
    self.assertEqual(as_pacific.tzinfo, None)


  def testBasicUse(self):
    tz = 'America/Los_Angeles'
    kbjson.TIME_ZONE = tz
    obj = kbjson.loads(SAMPLE_INPUT)
    print obj
    self.assertEqual(obj.event, "my-event")
    self.assertEqual(obj.sub.list, [1,2,3])

    expected = util.utc_to_local(datetime.datetime(2010, 6, 11, 23, 1, 1), tz)
    self.assertEqual(obj.iso_time, expected)
    self.assertEqual(obj.bad_time, "123-45")  # fails strptime

if __name__ == '__main__':
  unittest.main()

