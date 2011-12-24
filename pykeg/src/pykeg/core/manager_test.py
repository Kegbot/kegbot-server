#!/usr/bin/env python

"""Unittest for manager module"""

import unittest

from pykeg.core import kbevent
from pykeg.core import kb_common
from pykeg.core import manager

class _MockKegbotCore(object):
  pass

class FlowManagerTestCase(unittest.TestCase):
  def setUp(self):
    event_hub = kbevent.EventHub()
    self.tap_manager = manager.TapManager("tap-manager", event_hub)
    self.flow_manager = manager.FlowManager("flow-manager", event_hub, self.tap_manager)
    self.tap_manager.RegisterTap(name='flow0', ml_per_tick=1/2200.0,
        max_tick_delta=1100)

  def tearDown(self):
    self.tap_manager.UnregisterTap(name='flow0')

  def testBasicMeterUse(self):
    """Create a new flow device, perform basic operations on it."""
    # Duplicate registration should cause an exception.
    self.assertRaises(manager.AlreadyRegisteredError,
                      self.tap_manager.RegisterTap, 'flow0', 0, 0)

    # ...as should operations on an unknown device.
    self.assertRaises(manager.UnknownDeviceError,
                      self.tap_manager.GetTap, 'flow_unknown')
    self.assertRaises(manager.UnknownDeviceError,
                      self.tap_manager.UpdateDeviceReading, 'flow_unknown', 123)

    # Our new device should have accumulated 0 volume thus far.
    tap = self.tap_manager.GetTap(name='flow0')
    meter = tap.GetMeter()
    self.assertEqual(meter.GetTicks(), 0L)

    # Report an instantaneous reading of 2000 ticks. Since this is the first
    # reading, this should cause no change in the device volume.
    self.tap_manager.UpdateDeviceReading(name='flow0', value=2000)
    self.assertEqual(meter.GetTicks(), 0L)

    # Report another instantaneous reading, which should now increment the flow
    self.tap_manager.UpdateDeviceReading(name='flow0', value=2100)
    self.assertEqual(meter.GetTicks(), 100L)

    # The FlowManager saves the last reading value; check it.
    self.assertEqual(meter.GetLastReading(), 2100)

    # Report a reading that is much larger than the last reading. Values larger
    # than the constant kb_common.MAX_METER_READING_DELTA should be ignored by
    # the FlowManager.
    illegal_delta = kb_common.MAX_METER_READING_DELTA + 100
    new_reading = last_reading + illegal_delta
    self.tap_manager.UpdateDeviceReading(name='flow0', value=new_reading)
    # The illegal update should not affect the volume.
    vol = self.flow_manager.GetDeviceVolume(name='flow0')
    self.assertEqual(vol, 100L)
    # The value of the last update should be recorded, however.
    last_reading = self.flow_manager.GetDeviceLastReading(name='flow0')
    self.assertEqual(last_reading, new_reading)

  def testOverflowHandling(self):
    first_reading = 2**32 - 100    # start with very large number
    second_reading = 2**32 - 50    # increment by 50
    overflow_reading = 10          # increment by 50+10 (overflow)

    self.tap_manager.UpdateDeviceReading('flow0', first_reading)
    curr_reading = self.flow_manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 0)

    self.tap_manager.UpdateDeviceReading('flow0', second_reading)
    curr_reading = self.flow_manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 50)

    self.tap_manager.UpdateDeviceReading('flow0', overflow_reading)
    curr_reading = self.flow_manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 110)

  def testNoOverflow(self):
    self.tap_manager.UpdateDeviceReading('flow0', 0)
    curr_reading = self.flow_manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 0)

    self.tap_manager.UpdateDeviceReading('flow0', 100)
    curr_reading = self.flow_manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 100)

    self.tap_manager.UpdateDeviceReading('flow0', 10)
    curr_reading = self.flow_manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 100)

    self.tap_manager.UpdateDeviceReading('flow0', 20)
    curr_reading = self.flow_manager.GetDeviceVolume('flow0')
    self.assertEqual(curr_reading, 110)

  def testActivityMonitoring(self):
    self.tap_manager.UpdateDeviceReading('flow0', 0, when=0)

    # initial idle time should be infinite (should return `now`)
    idle_time = self.flow_manager.GetDeviceIdleSeconds('flow0', now=1000)
    self.assertEqual(idle_time, 1000)

    self.tap_manager.UpdateDeviceReading('flow0', 10, when=10)
    self.tap_manager.UpdateDeviceReading('flow0', 30, when=15)

    idle_time = self.flow_manager.GetDeviceIdleSeconds('flow0', now=20)
    self.assertEqual(idle_time, 5)

    # Updating the device again with zero delta should not clear existing idle
    # time.
    self.tap_manager.UpdateDeviceReading('flow0', 30, when=30)
    idle_time = self.flow_manager.GetDeviceIdleSeconds('flow0', now=40)
    self.assertEqual(idle_time, 25)

    # Updating the device with negative delta should also leave idle time
    # unchanged.
    self.tap_manager.UpdateDeviceReading('flow0', 10, when=50)
    idle_time = self.flow_manager.GetDeviceIdleSeconds('flow0', now=60)
    self.assertEqual(idle_time, 45)


if __name__ == '__main__':
  unittest.main()
