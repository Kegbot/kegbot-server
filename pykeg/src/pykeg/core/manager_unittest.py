#!/usr/bin/env python

"""Unittest for manager module"""

import unittest

from pykeg.core import kb_common
from pykeg.core import manager

class _MockKegbotCore(object):
  pass

class FlowManagerTestCase(unittest.TestCase):
  def setUp(self):
    self.manager = manager.FlowManager()
    self.manager.RegisterDevice(name='flow0')

  def tearDown(self):
    self.manager.UnregisterDevice(name='flow0')

  def testBasicMeterUse(self):
    """Create a new flow device, perform basic operations on it."""
    # Duplicate registration should cause an exception.
    self.assertRaises(manager.AlreadyRegisteredError,
                      self.manager.RegisterDevice, 'flow0')

    # ...as should operations on an unknown device.
    self.assertRaises(manager.UnknownDeviceError,
                      self.manager.GetDeviceVolume, 'flow_unknown')
    self.assertRaises(manager.UnknownDeviceError,
                      self.manager.UpdateDeviceReading, 'flow_unknown', 123)

    # Our new device should have accumulated 0 volume thus far.
    reading = self.manager.GetDeviceVolume(name='flow0')
    self.assertEqual(reading, 0L)

    # Report an instantaneous reading of 2000 ticks. Since this is the first
    # reading, this should cause no change in the device volume.
    self.manager.UpdateDeviceReading(name='flow0', value=2000)
    reading = self.manager.GetDeviceVolume(name='flow0')
    self.assertEqual(reading, 0L)

    # Report another instantaneous reading, which should now increment the flow
    self.manager.UpdateDeviceReading(name='flow0', value=2100)
    reading = self.manager.GetDeviceVolume(name='flow0')
    self.assertEqual(reading, 100L)

    # The FlowManager saves the last reading value; check it.
    last_reading = self.manager.GetDeviceLastReading(name='flow0')
    self.assertEqual(last_reading, 2100)

    # Report a reading that is much larger than the last reading. Values larger
    # than the constant kb_common.MAX_METER_READING_DELTA should be ignored by
    # the FlowManager.
    illegal_delta = kb_common.MAX_METER_READING_DELTA + 100
    new_reading = last_reading + illegal_delta
    self.manager.UpdateDeviceReading(name='flow0', value=new_reading)
    # The illegal update should not affect the volume.
    vol = self.manager.GetDeviceVolume(name='flow0')
    self.assertEqual(vol, 100L)
    # The value of the last update should be recorded, however.
    last_reading = self.manager.GetDeviceLastReading(name='flow0')
    self.assertEqual(last_reading, new_reading)

  def testOverflowHandling(self):
    first_reading = 2**32 - 100    # start with very large number
    second_reading = 2**32 - 50    # increment by 50
    overflow_reading = 10          # increment by 50+10 (overflow)

    self.manager.UpdateDeviceReading('flow0', first_reading)
    curr_reading = self.manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 0)

    self.manager.UpdateDeviceReading('flow0', second_reading)
    curr_reading = self.manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 50)

    self.manager.UpdateDeviceReading('flow0', overflow_reading)
    curr_reading = self.manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 110)

  def testNoOverflow(self):
    self.manager.UpdateDeviceReading('flow0', 0)
    curr_reading = self.manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 0)

    self.manager.UpdateDeviceReading('flow0', 100)
    curr_reading = self.manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 100)

    self.manager.UpdateDeviceReading('flow0', 10)
    curr_reading = self.manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 100)

    self.manager.UpdateDeviceReading('flow0', 20)
    curr_reading = self.manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 110)

  def testActivityMonitoring(self):
    self.manager.UpdateDeviceReading('flow0', 0, when=0)

    # initial idle time should be infinite (should return `now`)
    idle_time = self.manager.GetDeviceIdleSeconds('flow0', now=1000)
    self.assertEqual(idle_time, 1000)

    self.manager.UpdateDeviceReading('flow0', 10, when=10)
    self.manager.UpdateDeviceReading('flow0', 30, when=15)

    idle_time = self.manager.GetDeviceIdleSeconds('flow0', now=20)
    self.assertEqual(idle_time, 5)

    # Updating the device again with zero delta should not clear existing idle
    # time.
    self.manager.UpdateDeviceReading('flow0', 30, when=30)
    idle_time = self.manager.GetDeviceIdleSeconds('flow0', now=40)
    self.assertEqual(idle_time, 25)

    # Updating the device with negative delta should also leave idle time
    # unchanged.
    self.manager.UpdateDeviceReading('flow0', 10, when=50)
    idle_time = self.manager.GetDeviceIdleSeconds('flow0', now=60)
    self.assertEqual(idle_time, 45)


if __name__ == '__main__':
  unittest.main()
