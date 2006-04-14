import sys
import time

from Devices import NoOp

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
   """
   A Channel is a path of beer contianing a flow controller and drinker queue.

   For example, the typical kegerator has only one keg and thus one channel. A
   4-headed kegerator would likely have 4 kegbot channels, each channel having
   its own flow controller instance and drinker "flow" queue.
   """
   def __init__(self, chanid, logger, valve_relay = None, flow_meter = None):
      self.chanid = id
      self.logger = logger

      if valve_relay is None:
         valve_relay = NoOp.Relay()
      self.valve_relay = valve_relay

      if flow_meter is None:
         flow_meter = NoOp.Flowmeter()
      self.flow_meter = flow_meter

      self.flow_queue = []
      self.active_flow = None

   def EnqueueFlow(self, flow):
      """ Add a flow to the waiting queue of flows """
      self.flow_queue.append(flow)

   def MaybeActivateNextFlow(self):
      """ If there isn't an active flow, pop one from flow_queue and activate """
      if self.active_flow is None:
         try:
            flow = self.flow_queue.pop()
         except:
            return None
         self.logger.info('new active flow: %s' % flow)
         self.active_flow = flow
         return flow
      return None

   def EnableValve(self):
      return self.valve_relay.Enable()

   def DisableValve(self):
      return self.valve_relay.Disable()

   def GetTicks(self):
      return self.flow_meter.GetTicks()

   def DeactivateFlow(self):
      """ Reset active_flow state variable to None """
      self.active_flow = None

