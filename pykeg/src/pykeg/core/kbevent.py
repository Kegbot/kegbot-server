# Copyright 2009 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Simple event-passing mechanisms.

This module implements a very simple inter-process event passing system
(EventHub), and corresponding message class (Event).
"""

import logging
import Queue

import gflags

from pykeg.core import kbjson
from pykeg.core import util

FLAGS = gflags.FLAGS

gflags.DEFINE_boolean('debug_events', False,
    'If true, logs debugging information about internal events.')

class Event(util.BaseMessage):
  def __init__(self, initial=None, encoded=None, **kwargs):
    util.BaseMessage.__init__(self, initial, **kwargs)
    if encoded is not None:
      self.DecodeFromString(encoded)

  def ToDict(self):
    data = {}
    for field_name, value in self._values.iteritems():
      data[field_name] = value

    ret = {
      'event': self.__class__.__name__,
      'data': data,
    }
    return ret

  def ToJson(self, indent=2):
    return kbjson.dumps(self.ToDict(), indent=indent)

EventField = util.BaseField

class Ping(Event):
  pass

class QuitEvent(Event):
  pass

class StartCompleteEvent(Event):
  pass

class MeterUpdate(Event):
  tap_name = EventField()
  reading = EventField()

class FlowUpdate(Event):
  class FlowState:
    INITIAL = "initial"
    ACTIVE = "active"
    IDLE = "idle"
    CLOSE_WAIT = "close_wait"
    COMPLETED = "completed"
  flow_id = EventField()
  tap_name = EventField()
  state = EventField()
  username = EventField()
  start_time = EventField()
  last_activity_time = EventField()
  ticks = EventField()
  volume_ml = EventField()

class TapIdleEvent(Event):
  tap_name = EventField()

class DrinkCreatedEvent(Event):
  flow_id = EventField()
  drink_id = EventField()
  tap_name = EventField()
  start_time = EventField()
  end_time = EventField()
  username = EventField()

class TokenAuthEvent(Event):
  class TokenState:
    ADDED = "added"
    REMOVED = "removed"
  tap_name = EventField()
  auth_device_name = EventField()
  token_value = EventField()
  status = EventField()

class ThermoEvent(Event):
  sensor_name = EventField()
  sensor_value = EventField()

class FlowRequest(Event):
  class Action:
    START_FLOW = "start_flow"
    STOP_FLOW = "stop_flow"
    REPORT_STATUS = "report_status"
  tap_name = EventField()
  request = EventField()

class HeartbeatSecondEvent(Event):
  pass

class HeartbeatMinuteEvent(Event):
  pass

class HeartbeatHourEvent(Event):
  pass

class SetRelayOutputEvent(Event):
  class Mode:
    ENABLED = "enabled"
    DISABLED = "disabled"
  output_name = EventField()
  output_mode = EventField()

class CreditAddedEvent(Event):
  amount = EventField()
  username = EventField()

EVENT_NAME_TO_CLASS = {}
for cls in Event.__subclasses__():
  name = cls.__name__
  EVENT_NAME_TO_CLASS[name] = cls

def DecodeEvent(msg):
  if isinstance(msg, basestring):
    msg = kbjson.loads(msg)
  event_name = msg.get('event')
  if event_name not in EVENT_NAME_TO_CLASS:
    raise ValueError, "Unknown event: %s" % event_name
  inst = EVENT_NAME_TO_CLASS[event_name]()
  for k, v in msg['data'].iteritems():
    setattr(inst, k, v)
  return inst

class EventHub(object):
  """Central sink and publish of events."""
  def __init__(self):
    self._event_listeners = set()
    self._event_queue = Queue.Queue()
    self._logger = logging.getLogger('eventhub')

  def AddListener(self, listener):
    """Attach a listener, to be notified on receipt of a new event.

    The listener must implement the PostEvent(event) method.
    """
    if listener not in self._event_listeners:
      self._event_listeners.add(listener)

  def RemoveListener(self, listener):
    """Remove (by reference) an already-listening listener."""
    if listener in self._event_listeners:
      self._event_listeners.remove(listener)

  def PublishEvent(self, event):
    """Add a new event to the queue of events to publish.

    Events are dispatched to listeners in the DispatchNextEvent method.
    """
    self._event_queue.put(event)

  def _IterEventListeners(self):
    """Iterate through all listeners."""
    for listener in self._event_listeners:
      yield listener

  def _WaitForEvent(self, timeout=None):
    """Wait for a new event to be enqueued."""
    try:
      ev = self._event_queue.get(block=True, timeout=timeout)
    except Queue.Empty:
      ev = None
    return ev

  def DispatchNextEvent(self, timeout=None):
    """Wait for an event, and dispatch it to all listeners."""
    ev = self._WaitForEvent(timeout)
    if ev:
      if FLAGS.debug_events:
        self._logger.debug('Publishing event: %s ' % ev)
      for listener in self._IterEventListeners():
        listener.PostEvent(ev)

