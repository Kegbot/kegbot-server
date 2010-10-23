#!/usr/bin/env python

"""Unittest for kbjson module"""

import datetime
import kbjson
import unittest

SAMPLE_INPUT = """
{
  "event": "my-event",
  "sub" : {
    "list" : [1,2,3]
  },
  "iso_time": "2010-06-11T23:25:16Z",
  "bad_time": "123-45"
}
"""

class JsonTestCase(unittest.TestCase):
  def setUp(self):
    pass

  def testBasicUse(self):
    obj = kbjson.loads(SAMPLE_INPUT)
    print obj
    self.assertEqual(obj.event, "my-event")
    self.assertEqual(obj.sub.list, [1,2,3])

    expected_date = datetime.datetime(2010, 6, 11, 23, 25, 16)
    self.assertEqual(obj.iso_time, expected_date)
    self.assertEqual(obj.bad_time, "123-45")  # fails strptime

if __name__ == '__main__':
  unittest.main()

