import datetime
import logging
import math
import threading
import time

from pykeg.core import kb_common
from pykeg.core import units

class FlowManagerError(Exception):
  """ Generic FlowManager error """


class AlreadyRegisteredError(FlowManagerError):
  """ Raised when attempting to register an already-registered name """


class UnknownDeviceError(FlowManagerError):
  """ Raised when device name given does not exist """


class FlowManager(object):

  class Flow(object):
    def __init__(self, start_volume, when=None):
      self._start_volume = start_volume
      self._last_volume = start_volume
      self._SetLastActivity(when)
      self._start_time = self._last_activity

    def __str__(self):
      return "[Flow vol=%i/%i]" % (self._start_volume, self._last_volume)

    def _SetLastActivity(self, when):
      if not when:
        when = datetime.datetime.now()
      self._last_activity = when

    def SetVolume(self, volume, when=None):
      if volume > self._last_volume:
        self._SetLastActivity(when)
        self._last_volume = volume

    def IncVolume(self, volume, when=None):
      if volume > 0:
        self._SetLastActivity(when)
        self._last_volume += volume

    def GetVolume(self):
      amt = self._last_volume - self._start_volume
      return units.Quantity(amt, units.UNITS.KbMeterTick)

    def GetStartTime(self):
      return self._start_time

    def GetEndTime(self):
      return self._last_activity

    def GetKeg(self):
      return None

    def GetUser(self):
      return None


  def __init__(self):
    self._logger = logging.getLogger('flowmanager')
    self._flow_lock = threading.Lock()
    self._total_volume_map = {}
    self._last_reading_map = {}
    self._flow_map = {}
    self._flow_update_event = threading.Event()

  def _DeviceExists(self, name):
    return name in self._total_volume_map

  def _CheckDeviceExists(self, name):
    if not self._DeviceExists(name):
      raise UnknownDeviceError

  def RegisterDevice(self, name):
    if self._DeviceExists(name):
      raise AlreadyRegisteredError

    self._logger.info('Registered new device: %s' % name)
    self._total_volume_map[name] = 0L
    self._last_reading_map[name] = None
    self._flow_map[name] = None

  def UnregisterDevice(self, name):
    self._CheckDeviceExists(name)
    ret = self._last_reading_map.get(name)
    del self._total_volume_map[name]
    del self._last_reading_map[name]
    del self._flow_map[name]
    self._logger.info('Unregistered device: %s' % name)
    return ret

  def EndFlow(self, name):
    ret = None
    self._flow_lock.acquire()
    if name in self._flow_map:
      ret = self._flow_map[name]
      self._flow_map[name] = None
    self._flow_lock.release()
    return ret

  def GetDeviceVolume(self, name):
    self._CheckDeviceExists(name)
    return self._total_volume_map[name]

  def GetDeviceLastReading(self, name):
    self._CheckDeviceExists(name)
    return self._last_reading_map[name]

  def WaitForUpdate(self, timeout=None):
    self._flow_update_event.wait(timeout)

  def UpdateDeviceReading(self, name, value, when=None):
    self._CheckDeviceExists(name)
    self._logger.info('Update reading: %s=%s' % (name, value))

    value = long(value)
    if value < 0:
      raise ValueError, "UpdateDeviceReading only accepts positive values"

    self._flow_lock.acquire() # TODO: make me a decorator

    last_reading = self._last_reading_map[name]
    self._last_reading_map[name] = value

    if last_reading is None:
      last_reading = value

    is_new_flow = False
    flow_obj = self._flow_map.get(name)
    if flow_obj is None:
      flow_obj = FlowManager.Flow(value)
      self._flow_map[name] = flow_obj
      is_new_flow = True

    if value >= last_reading:
      # Normal case: zero or positive delta from last reading.
      delta = value - last_reading
    else:
      # Possible overflow. Resolution algorithm: assume overflow occured at
      # the next power of two following the last reading. Compute the delta to
      # be the difference between last_reading and that power of two, plus
      # whatever the current reading is.
      #
      # This may assume overflow where non occured; for example, if the meter
      # was suddenly reset. MAX_METER_READING_DELTA should be low enough to
      # mitigate this problem.
      for power_of_two in (2**16, 2**32, 2**64):
        if last_reading < power_of_two:
          break
      delta = power_of_two - last_reading + value

    # If there was actually a change, increment total volume and update activity
    # time.
    if delta > 0 and delta <= kb_common.MAX_METER_READING_DELTA:
      self._total_volume_map[name] += delta
      flow_obj.IncVolume(delta)
      self._flow_update_event.set()
      self._flow_update_event.clear()
    elif delta > kb_common.MAX_METER_READING_DELTA:
      self._logger.warning('Tick delta exceeds maximum allowed; %i > %i' %
          (delta, kb_common.MAX_METER_READING_DELTA))

    self._flow_lock.release()
    return flow_obj, is_new_flow
