#!/usr/bin/env python

"""Unittest for alarm module"""

import unittest
import time

from pykeg.core import alarm

class MainTestCase(unittest.TestCase):
  def setUp(self):
    self.am = alarm.AlarmManager()

  def testBasicUse(self):
    """Creates alarms out-of-order and ensures they fire in-order."""
    self.assert_(self.am)
    a1 = self.am.AddAlarm("test1", 1.0, None)
    a3 = self.am.AddAlarm("test3", 3.0, None)
    a2 = self.am.AddAlarm("test2", 2.0, None)

    now = time.time()
    ret = self.am.WaitForNextAlarm(4.0)
    self.assertEqual(ret, a1)
    ret = self.am.WaitForNextAlarm(4.0)
    self.assertEqual(ret, a2)
    ret = self.am.WaitForNextAlarm(4.0)
    self.assertEqual(ret, a3)

    print ret

  def testTimerEmptyList(self):
    """Verify an empty alarm manager waits appropriately."""
    start = time.time()
    self.am.WaitForNextAlarm(1.0)
    self.assert_((start + 1.0) <= time.time())


if __name__ == '__main__':
  unittest.main()
