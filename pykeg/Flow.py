import logging
import sys
import time
import Queue

from Devices import NoOp

class Flow:
   """ Holds all the state of a flow/pour """
   def __init__(self, channel, start = None, user = None,
         ticks = 0, max_volume = sys.maxint, end = None):
      self.channel = channel
      self.start = start or time.time()
      self.end = end or start
      self.user = user
      self._ticks = ticks
      self.max_volume = max_volume

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

   def Keg(self):
      return self.channel.GetKeg()

class Channel:
   """
   A Channel is a path of beer contianing a flow controller and drinker queue.

   For example, the typical kegerator has only one keg and thus one channel. A
   4-tap kegbot would have 4 channels, each channel having its own flow
   controller instance and drinker "flow" queue.
   """
   def __init__(self, chanid, valve_relay = None, flow_meter = None):
      self.chanid = id
      self.logger = logging.getLogger('channel%s' % str(chanid))

      if valve_relay is None:
         valve_relay = NoOp.Relay()
      assert isinstance(Interfaces.IRelay), "valve_relay must implement IRelay interface"
      self.valve_relay = valve_relay

      if flow_meter is None:
         flow_meter = NoOp.Flowmeter()
      assert isinstance(Interfaces.IFlowmeter), "flow_meter must implement IFlowmeter interface"
      self.flow_meter = flow_meter

      self.flow_queue = Queue.Queue()
      self.active_flow = None

   def EnqueueFlow(self, flow):
      """ Add a flow to the waiting queue of flows """
      self.flow_queue.put(flow)

   def MaybeActivateNextFlow(self):
      """ If there isn't an active flow, pop one from flow_queue and activate """
      if self.active_flow is not None:
         return None
      try:
         flow = self.flow_queue.get_nowait()
      except Queue.Empty:
         return None
      self.logger.info('new active flow: %s' % flow)
      self.active_flow = flow
      return flow

   def EnableValve(self):
      return self.valve_relay.Enable()

   def DisableValve(self):
      return self.valve_relay.Disable()

   def GetTicks(self):
      return self.flow_meter.GetTicks()

   def DeactivateFlow(self):
      """ Reset active_flow state variable to None """
      self.active_flow = None

   def GetKeg(self):
      online_kegs = list(Backend.Keg.selectBy(status='online',
         channel=self.chanid, orderBy='-id'))
      if len(online_kegs) == 0:
         return None
      else:
         return online_kegs[0]

