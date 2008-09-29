import logging
import sys
import datetime
import time
import Queue

from django.db.models import base

from pykeg.core import kb_common
from pykeg.core import models
from pykeg.core import Interfaces
from pykeg.core import units
from pykeg.core import util
from pykeg.core.Devices import NoOp

FLOW_EVENT = util.Enum(*(
  'FLOW_START',
  'FLOW_UPDATE',
  'FLOW_END',
))

class Flow:
   """
   Holds all the state of a flow/pour.

   The main Kegbot class is responsible for associating a Flow object with a
   particular channel, and updating the data in this object by servicing the
   Flow periodically.
   """
   def __init__(self, channel, user, keg, start=None, ticks=0, end=None):
      self.channel = channel
      self.start = start or datetime.datetime.now()
      self.end = end or self.start
      self.user = user
      self._ticks = ticks

      self._last_activity = time.time()
      self._last_ticks = None
      self._keg = keg

   def __str__(self):
     return '<Flow channel=%s user=%s keg=%s ticks=%s>' % (self.channel,
                                                           self.user,
                                                           self._keg,
                                                           self._ticks)

   def keg(self):
     return self._keg

   def IncTicks(self, delta):
     self._ticks += delta
     if delta:
       self._last_activity = time.time()

   def IdleSeconds(self):
      return time.time() - self._last_activity

   def Ticks(self):
      return self._ticks

   def Volume(self):
      return units.Quantity(self._ticks, units.UNITS.KbMeterTick)


class Channel:
   def __init__(self, channel_id, event_queue, valve_relay=None,
                flow_meter=None):
      self._channel_id = str(channel_id)
      self._event_queue = event_queue
      self._logger = logging.getLogger('channel%s' % self._channel_id)

      # possible channel states:
      #  idle    - ready for a flow
      #  pouring - actively being serviced by pykeg
      #  failed  - the channel is unserviceable
      self.state = 'init'
      self.SetState('idle')

      if valve_relay is None:
         valve_relay = NoOp.Relay()
      assert isinstance(valve_relay,Interfaces.IRelay), \
            "valve_relay must implement IRelay interface"
      self._valve_relay = valve_relay

      if flow_meter is None:
         flow_meter = NoOp.Flowmeter()
      assert isinstance(flow_meter, Interfaces.IFlowmeter),\
            "flow_meter must implement IFlowmeter interface"
      self._flow_meter = flow_meter

      self._waiting = Queue.Queue()
      self._last_ticks = self.GetTicks()

   def __str__(self):
     return self.channel_id()

   def channel_id(self):
     return self._channel_id

   def IsIdle(self):
      return self.state == "idle"

   def SetState(self, state):
      self._logger.info('state change [%s] -> [%s]' % (self.state, state))
      self.state = state

   def IsFailed(self):
      return self.state == "failed"

   def IsActive(self):
      return self.state == "pouring"

   def _StartFlow(self, f):
      assert self.IsIdle(), "Trying to start flow when not idle"
      self.SetState('pouring')

   def _EndFlow(self):
      assert self.IsActive(), "Trying to end flow when not active"
      self.SetState('idle')

   def Service(self):
      now_ticks = self.GetTicks()
      delta_ticks = now_ticks - self._last_ticks
      self._last_ticks = now_ticks

      if delta_ticks < 0:
         # TODO: overflow?
         return False
      elif self.IsFailed():
         return False

      if delta_ticks:
        self._PushChannelEvent(delta_ticks)

   def _PushChannelEvent(self, ticks):
     evnum = kb_common.KB_EVENT.CHANNEL_ACTIVITY
     evdata = {
         'channel_id': self.channel_id(),
         'ticks': ticks,
     }
     self._event_queue.put((evnum, evdata))

   def StartFlow(self):
      return self._valve_relay.Enable()

   def StopFlow(self):
      self._valve_relay.Disable()
      self.end = datetime.datetime.now()
      self._last_ticks = self.GetTicks()

   def GetTicks(self):
      return self._flow_meter.GetTicks()

   def DeactivateFlow(self):
      self.SetState('idle')
