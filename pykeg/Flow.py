import logging
import sys
import datetime
import time
import Queue

from pykeg.core import models
from Devices import NoOp
import Interfaces
import util

class Flow:
   """
   Holds all the state of a flow/pour.

   The main Kegbot class is responsible for associating a Flow object with a
   particular channel, and updating the data in this object by servicing the
   Flow periodically.
   """
   def __init__(self, channel, start = None, user = None,
         ticks = 0, max_volume = sys.maxint, end = None):
      self.channel = channel
      self.start = start or datetime.datetime.now()
      self.end = end or self.start
      self.user = user
      self._ticks = ticks
      self.max_volume = max_volume
      self.est_cost = 0.0

      self._last_activity = time.time()
      self._last_ticks = None

   def SetTicks(self, ticks):
      """
      Set or increment the tick count (warning: not idempotent, see note!)

      For this flow, if this is the first time SetTicks is called, then the
      Flow is 'zeroed' around this value.

      Subsequent calls to SetTicks will cause the current flow's tick countere
      to be incremented by difference between the current value of `ticks`, and
      the value at the last function call.
      """
      if self._last_ticks is None:
         self._last_ticks = ticks

      # compute difference with respect to last call, and log a warning if so.
      # IFlowmeter devices should be insulating us from this situation, so this
      # is an unusal error. (handling of wraparound cases may be possible, but
      # should still be the responsiblity of an IFlowmeter implementation)
      diff = ticks - self._last_ticks
      if diff < 0:
         self.channel.logger.warning('Tick value to SetTicks (%s) less than last call (%s); ignoring)' % (ticks, self._last_ticks))
         diff = 0

      self._ticks += diff
      self._last_ticks = ticks
      if diff != 0:
         self._last_activity = time.time()
      return diff

   def IdleSeconds(self):
      return time.time() - self._last_activity

   def Ticks(self):
      return self._ticks


class Channel:
   """
   A Channel is a path of beer containing flow control and a drinker queue.

   For example, the typical kegerator has only one keg and thus one channel. A
   4-tap kegbot would have 4 channels, each channel having its own flow
   controller instance and drinker "flow" queue.

   Every controlled beer line is associated with exactly one channel. While a
   flow is in progress, there is exactly one Flow object associated with that
   channel, dynamically created to store data about the current pour. Each

   A flow is created in one of two ways. First, each channel maintains a queue
   of waiting users. When a user arrives on the channel, if the channel is
   idle, a new flow is created for that user and started. If the channel is
   busy, the user waits in a queue until the channel is free or the user goes
   away.

   If the channel detects a flow has started without a user arriving, it starts
   a new flow with an anonymous user.

   For convenience, the channel class contains a reference (whose value may
   possibly be None) to the current active Flow, if any.
   """
   def __init__(self, chanid, valve_relay = None, flow_meter = None,
         allow_anon = True):
      self.chanid = chanid
      self.logger = logging.getLogger('channel%s' % str(chanid))


      # possible channel states:
      #  idle    - ready for a flow
      #  pouring - actively being serviced by pykeg
      #  failed  - the channel is unserviceable
      self.state = "idle"

      if valve_relay is None:
         valve_relay = NoOp.Relay()
      assert isinstance(valve_relay,Interfaces.IRelay), \
            "valve_relay must implement IRelay interface"
      self.valve_relay = valve_relay

      if flow_meter is None:
         flow_meter = NoOp.Flowmeter()
      assert isinstance(flow_meter, Interfaces.IFlowmeter),\
            "flow_meter must implement IFlowmeter interface"
      self.flow_meter = flow_meter

      # cache locally what user to use for anonymous flows, if any (if no user
      # has the label 'guest', anonymous flows will be disabled)
      self.anon_user = None
      if allow_anon:
         for user in models.User.objects.all():
            try:
               p = user.get_profile()
            except AttributeError:
               p = None # XXX django thorws an expection if profile does not exist
            print p
            if p and p.HasLabel('guest'):
               self.anon_user = user
         if self.anon_user is not None:
            self.logging.info('Anonymous user: %s' % self.anon_user)
         else:
            self.logger.warning('Anonymous user not found!')
      else:
         self.logger.info('Anonymous users are not permitted')

      self._waiting = Queue.Queue()
      self.active_flow = None
      self._last_ticks = self.GetTicks()
      self._idle_stats = util.TimeStats(10)

   def IsIdle(self):
      return self.state == "idle"

   def SetState(self, state):
      self.logger.info('state change [%s] -> [%s]' % (self.state, state))
      self.state = state

   def IsFailed(self):
      return self.state == "failed"

   def IsActive(self):
      return self.state == "pouring"

   def _StartFlow(self, f):
      assert self.IsIdle(), "Trying to start flow when not idle"
      self.active_flow = f
      self.state = "pouring"

   def _EndFlow(self):
      assert self.IsActive(), "Trying to end flow when not active"

   def EnqueueUser(self, user):
      """ Add a user to the queue of waiting users """
      self._waiting.put(user)

   def _CreateFlow(self, user):
      return Flow(self, user=user, max_volume=user.MaxVolume())

   def _GetUserForNewFlow(self):
      """ Called when a flow starts and returns who to blame """
      if not self._waiting.empty():
         return self._waiting.get_nowait()
      else:
         return self.anon_user

   def _GetAndIncrementFlow(self, ticks):
      """ Fetch the current flow (possibly creating it) and increment it """
      if self.IsIdle():
         flow_user = self._GetUserForNewFlow()
         if not flow_user:
            # TODO: should we allow this?
            return False
         self.logger.info('creating new flow for user %s' % flow_user)
         self._StartFlow(self._CreateFlow(flow_user))
      if self.IsActive():
         return self.active_flow.SetTicks(ticks)
      else:
         return False

   def Service(self):
      now_ticks = self.GetTicks()
      delta_ticks = now_ticks - self._last_ticks

      # do nothing if the delta was zero and there are no users waiting. bail
      # out if we're in failed state, too.
      if delta_ticks <= 0 and self._waiting.empty():
         self._last_ticks = now_ticks
         return False
      elif self.IsFailed():
         return False

      # increment the flow. this may create the flow if there is new activity,
      # or if there is a new waiting user (we create a flow whether or not
      # there is activity)
      diff = self._GetAndIncrementFlow(now_ticks)
      flow = self.active_flow

      if not flow:
         self.logger.warning('no flow after tick increment, BUG')
         self.SetState('failed')
         return False

      # if anonymous flow, attempt to assign blame
      if flow.user == self.anon_user:
         if not self._waiting.empty():
            new_user = self._GetUserForNewFlow()
            self.logger.info('user %s replacing anonymous' % new_user.username)
            self.active_flow.user = new_user
            self.active_flow.max_volume = new_user.MaxVolume()

      self._last_ticks = now_ticks

   def StartFlow(self):
      self.logger.info('starting new flow for user %s' % self.active_flow.user.username)
      self.active_flow.SetTicks(self.GetTicks())
      return self.valve_relay.Enable()

   def StopFlow(self):
      self.valve_relay.Disable()
      self.end = datetime.datetime.now()
      self._last_ticks = self.GetTicks()
      self._idle_stats.Clear()

   def GetTicks(self):
      return self.flow_meter.GetTicks()

   def DeactivateFlow(self):
      """ Reset active_flow state variable to None """
      self.active_flow = None

   def Keg(self):
      channel_kegs = models.Keg.objects.filter(status='online',
            channel=self.chanid)
      if channel_kegs.count() != 1:
         return None
      return channel_kegs[0]

