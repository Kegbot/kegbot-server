import sys
import time

class Flow:
   """ Holds all the state of a flow/pour """
   def __init__(self, channel, start = None, user = None,
         ticks = 0, max_volume = sys.maxint, end = None,
         initial_ticks = None, keg = None):
      self.channel = channel
      self.start = start or time.time()
      self.end = end or time.time()
      self.user = user
      self._ticks = ticks
      self.max_volume = max_volume
      self.keg = keg

      self._last_activity = time.time()
      self._last_ticks = None

   def SetTicks(self, ticks):
      """ ticks should be a monotonically increasing count """
      if self._last_ticks is None:
         self._last_ticks = ticks

      diff = ticks - self._last_ticks
      self._ticks += diff
      self._last_activity = time.time()
      self._last_ticks = ticks
      return diff

   def IdleSeconds(self):
      return time.time() - self._last_activity

   def Ticks(self):
      return self._ticks

class Channel:
   def __init__(self, fc):
      self.fc = fc
