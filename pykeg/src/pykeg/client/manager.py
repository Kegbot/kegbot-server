# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

"""Tap (single path of fluid) management module."""

import datetime
import inspect
import time
import threading
import logging

from pykeg.core import backend
from pykeg.core import flow_meter
from pykeg.core import kb_common
from pykeg.core import kbevent
from pykeg.core import util


class TapManagerError(Exception):
  """ Generic TapManager error """

class AlreadyRegisteredError(TapManagerError):
  """ Raised when attempting to register an already-registered name """

class UnknownTapError(TapManagerError):
  """ Raised when tap requested does not exist """


def EventHandler(event_type):
  def decorate(f):
    if not hasattr(f, 'events'):
      f.events = set()
    f.events.add(event_type)
    return f
  return decorate


class Manager:
  def __init__(self, name, event_hub):
    self._name = name
    self._event_hub = event_hub
    self._logger = logging.getLogger(self._name)

  def GetEventHandlers(self):
    ret = {}
    for name, method in inspect.getmembers(self, inspect.ismethod):
      if not hasattr(method, 'events'):
        continue
      for event_type in method.events:
        if event_type not in ret:
          ret[event_type] = set()
        ret[event_type].add(method)
    return ret

  def _PublishEvent(self, event):
    """Convenience alias for EventHub.PublishEvent"""
    self._event_hub.PublishEvent(event)


class Tap:
  def __init__(self, name, ml_per_tick, max_tick_delta, relay_name=None):
    self._name = name
    self._ml_per_tick = ml_per_tick
    self._meter = flow_meter.FlowMeter(name, max_delta=max_tick_delta)
    self._relay_name = relay_name

  def __str__(self):
    return self._name

  def GetName(self):
    return self._name

  def GetMeter(self):
    return self._meter

  def GetRelayName(self):
    return self._relay_name

  def TicksToMilliliters(self, amt):
    return self._ml_per_tick * float(amt)


class TapManager(Manager):
  """Maintains listing of available fluid paths.

  This manager maintains the set of available beer taps.  Taps have a
  one-to-one correspondence with beer taps.  For example, a kegboard controller
  is capable of reading from two flow sensors; thus, it provides two beer
  taps.
  """

  def __init__(self, name, event_hub):
    Manager.__init__(self, name, event_hub)
    self._taps = {}

  def TapExists(self, name):
    return name in self._taps

  def GetAllTaps(self):
    return self._taps.values()

  def _CheckTapExists(self, name):
    if not self.TapExists(name):
      raise UnknownTapError

  def RegisterTap(self, name, ml_per_tick, max_tick_delta, relay_name=None):
    self._logger.info('Registering new tap: %s' % name)
    if self.TapExists(name):
      raise AlreadyRegisteredError
    self._taps[name] = Tap(name, ml_per_tick, max_tick_delta, relay_name)

  def UnregisterTap(self, name):
    self._logger.info('Unregistering tap: %s' % name)
    self._CheckTapExists(name)
    del self._taps[name]

  def GetTap(self, name):
    self._CheckTapExists(name)
    return self._taps[name]

  def UpdateDeviceReading(self, name, value, when=None):
    meter = self.GetTap(name).GetMeter()
    delta = meter.SetTicks(value, when=when)
    return delta


class Flow:
  def __init__(self, tap, flow_id, username=None, max_idle_secs=10):
    self._tap = tap
    self._flow_id = flow_id
    self._bound_username = username
    self._max_idle = datetime.timedelta(seconds=max_idle_secs)
    self._state = kbevent.FlowUpdate.FlowState.INITIAL
    self._start_time = datetime.datetime.now()
    self._end_time = None
    self._last_log_time = None
    self._total_ticks = 0L

  def __str__(self):
    return '<Flow 0x%08x: tap=%s ticks=%s username=%s max_idle=%s>' % (self._flow_id,
        self._tap, self._total_ticks, repr(self._bound_username),
        self._max_idle)

  def GetUpdateEvent(self):
    event = kbevent.FlowUpdate()
    event.flow_id = self._flow_id
    event.tap_name = self._tap.GetName()
    event.state = self._state

    # TODO(mikey): username or user_name in the proto, not both
    if self._bound_username:
      event.username = self._bound_username

    event.start_time = self._start_time
    end = self._start_time
    if self._end_time:
      end = self._end_time
    event.last_activity_time = end
    event.ticks = self.GetTicks()
    event.volume_ml = self.GetVolumeMl()

    return event

  def AddTicks(self, amount, when=None):
    self._total_ticks += amount
    if when is None:
      when = datetime.datetime.now()
    self._end_time = when

  def GetId(self):
    return self._flow_id

  def GetState(self):
    return self._state

  def SetState(self, state):
    self._state = state

  def SetMaxIdle(self, max_idle_secs):
    self._max_idle = datetime.timedelta(seconds=max_idle_secs)

  def GetTicks(self):
    return self._total_ticks

  def GetVolumeMl(self):
    return self._tap.TicksToMilliliters(self._total_ticks)

  def GetUsername(self):
    return self._bound_username

  def SetUsername(self, username):
    self._bound_username = username

  def GetStartTime(self):
    return self._start_time

  def GetEndTime(self):
    return self._end_time

  def GetIdleTime(self):
    end_time = self._end_time
    if end_time is None:
      end_time = self._start_time
    return datetime.datetime.now() - end_time

  def GetMaxIdleTime(self):
    return self._max_idle

  def GetTap(self):
    return self._tap

  def IsIdle(self):
    return self.GetIdleTime() > self.GetMaxIdleTime()


class FlowManager(Manager):
  """Class reponsible for maintaining and servicing flows.

  The manager is responsible for creating Flow instances and managing their
  lifecycle.  It is one layer above the the TapManager, in that it does not
  deal with devices directly.

  Flows can be started in multiple ways:
    - Explicitly, by a call to StartFlow
    - Implicitly, by a call to HandleTapActivity
  """
  def __init__(self, name, event_hub, tap_manager):
    Manager.__init__(self, name, event_hub)
    self._tap_manager = tap_manager
    self._flow_map = {}
    self._logger = logging.getLogger("flowmanager")
    self._next_flow_id = int(time.time())
    self._lock = threading.Lock()

  @util.synchronized
  def _GetNextFlowId(self):
    """Returns the next usable flow identifier.

    Flow IDs are simply sequence numbers, used around the core to disambiguate
    flows."""
    ret = self._next_flow_id
    self._next_flow_id += 1
    return ret

  def GetActiveFlows(self):
    return self._flow_map.values()

  def GetFlow(self, tap_name):
    return self._flow_map.get(tap_name)

  def StartFlow(self, tap_name, username='', max_idle_secs=10):
    try:
      tap = self._tap_manager.GetTap(tap_name)
    except UnknownTapError:
      return None

    current = self.GetFlow(tap_name)
    if current and username and current.GetUsername() != username:
      # There's an existing flow: take it over if anonymous; end it if owned by
      # another user.
      if current.GetUsername() == '':
        self._logger.info('User "%s" is taking over the existing flow' %
            username)
        self.SetUsername(current, username)
      else:
        self._logger.info('User "%s" is replacing the existing flow' %
            username)
        self.StopFlow(tap_name, disable_relay=False)
        current = None

    if current and current.GetUsername() == username:
      # Existing flow owned by this username.  Just poke it.
      current.SetMaxIdle(max_idle_secs)
      self._PublishUpdate(current)
      return current
    else:
      # No existing flow; start a new one.
      new_flow = Flow(tap, flow_id=self._GetNextFlowId(), username=username,
          max_idle_secs=max_idle_secs)
      self._flow_map[tap_name] = new_flow
      self._logger.info('Starting flow: %s' % new_flow)
      self._PublishUpdate(new_flow)

      # Open up the relay if the flow is authenticated.
      if username:
        self._PublishRelayEvent(new_flow, enable=True)
      return new_flow

  def SetUsername(self, flow, username):
    flow.SetUsername(username)
    self._PublishUpdate(flow)

  def StopFlow(self, tap_name, disable_relay=True):
    try:
      flow = self.GetFlow(tap_name)
    except UnknownTapError:
      return None
    if not flow:
      return None

    self._logger.info('Stopping flow: %s' % flow)
    self._PublishRelayEvent(flow, enable=False)
    tap = flow.GetTap()
    del self._flow_map[tap_name]
    self._StateChange(flow, kbevent.FlowUpdate.FlowState.COMPLETED)
    return flow

  def UpdateFlow(self, tap_name, meter_reading):
    try:
      tap = self._tap_manager.GetTap(tap_name)
    except TapManagerError:
      # tap is unknown or not available
      # TODO(mikey): guard against this happening
      return None, None

    delta = self._tap_manager.UpdateDeviceReading(tap.GetName(), meter_reading)
    self._logger.debug('Flow update: tap=%s meter_reading=%i (delta=%i)' %
        (tap_name, meter_reading, delta))

    if delta == 0:
      return None, None

    is_new = False
    flow = self.GetFlow(tap_name)
    if flow is None:
      self._logger.debug('Starting flow implicitly due to activity.')
      flow = self.StartFlow(tap_name)
      is_new = True
    flow.AddTicks(delta, datetime.datetime.now())

    if flow.GetState() != kbevent.FlowUpdate.FlowState.ACTIVE:
      self._StateChange(flow, kbevent.FlowUpdate.FlowState.ACTIVE)
    else:
      self._PublishUpdate(flow)

    return flow, is_new

  def _StateChange(self, flow, new_state):
    flow.SetState(new_state)
    self._PublishUpdate(flow)

  def _PublishUpdate(self, flow):
    event = flow.GetUpdateEvent()
    self._PublishEvent(event)

  @EventHandler(kbevent.MeterUpdate)
  def HandleFlowActivityEvent(self, event):
    """Handles the FLOW_DEV_ACTIVITY event.

    The handler accquires the FlowManager, and calls FlowUpdate.  This may
    result in one of three outcomes:
      - New flow created. A FLOW_START event is emitted, followed by a
        FLOW_UPDATE event.
      - Existing flow updated. A FLOW_UPDATE event is emitted.
      - Update refused.  The channel is unknown by the FlowManager.  No events
        are emitted.
    """
    try:
      flow_instance, is_new = self.UpdateFlow(event.tap_name, event.reading)
    except UnknownTapError:
      return None

  @EventHandler(kbevent.HeartbeatSecondEvent)
  def _HandleHeartbeatEvent(self, event):
    for flow in self.GetActiveFlows():
      tap = flow.GetTap()
      if flow.IsIdle():
        self._logger.info('Flow has become too idle, ending: %s' % flow)
        self._StateChange(flow, kbevent.FlowUpdate.FlowState.IDLE)
        self.StopFlow(flow.GetTap().GetName())
      else:
        if tap.GetRelayName():
          if flow.GetUsername():
            self._PublishRelayEvent(flow, enable=True)

  def _PublishRelayEvent(self, flow, enable=True):
    self._logger.debug('Publishing relay event: flow=%s, enable=%s' % (flow,
        enable))
    tap = flow.GetTap()
    relay = tap.GetRelayName()
    if not relay:
      self._logger.debug('No relay for this tap')
      return

    self._logger.debug('Relay for this tap: %s' % relay)
    if enable:
      mode = kbevent.SetRelayOutputEvent.Mode.ENABLED
    else:
      mode = kbevent.SetRelayOutputEvent.Mode.DISABLED
    ev = kbevent.SetRelayOutputEvent(output_name=relay, output_mode=mode)
    self._PublishEvent(ev)

  @EventHandler(kbevent.FlowRequest)
  def _HandleFlowRequestEvent(self, event):
    if event.request == event.Action.START_FLOW:
      self.StartFlow(event.tap_name)
    elif event.request == event.Action.STOP_FLOW:
      self.StopFlow(event.tap_name)


class DrinkManager(Manager):
  def __init__(self, name, event_hub, backend):
    Manager.__init__(self, name, event_hub)
    self._backend = backend

  @EventHandler(kbevent.FlowUpdate)
  def HandleFlowUpdateEvent(self, event):
    """Attempt to save a drink record and derived data for |flow|"""
    if event.state == event.FlowState.COMPLETED:
      self._HandleFlowEnded(event)

  def _HandleFlowEnded(self, event):
    self._logger.info('Flow completed: flow_id=0x%08x' % event.flow_id)

    ticks = event.ticks
    username = event.username
    volume_ml = event.volume_ml
    tap_name = event.tap_name
    pour_time = event.last_activity_time
    duration = (event.last_activity_time - event.start_time).seconds
    flow_id = event.flow_id

    # TODO: add to flow event
    auth_token = None

    if volume_ml <= kb_common.MIN_VOLUME_TO_RECORD:
        self._logger.info('Not recording flow: volume (%i mL) <= '
            'MIN_VOLUME_TO_RECORD (%i)' % (volume_ml, kb_common.MIN_VOLUME_TO_RECORD))
        return

    # Log the drink.  If the username is empty or invalid, the backend will
    # assign it to the default (anonymous) user.  The backend will assign the
    # drink to a keg.
    d = self._backend.RecordDrink(tap_name, ticks=ticks, username=username,
        pour_time=pour_time, duration=duration, auth_token=auth_token,
        spilled=False)

    if not d:
      self._logger.warning('No drink recorded.')
      return

    keg_id = d.keg_id or None
    username = d.user_id or '<None>'

    self._logger.info('Logged drink %s username=%s keg=%s liters=%.2f ticks=%i' % (
      d.id, username, keg_id, d.volume_ml/1000.0, d.ticks))

    # notify listeners
    created = kbevent.DrinkCreatedEvent()
    created.flow_id = flow_id
    created.drink_id = d.id
    created.tap_name = tap_name
    created.start_time = d.pour_time
    created.end_time = d.pour_time
    if d.user_id:
      created.username = d.user_id
    self._PublishEvent(created)


class ThermoManager(Manager):
  def __init__(self, name, event_hub, backend):
    Manager.__init__(self, name, event_hub)
    self._backend = backend
    self._name_to_last_record = {}
    self._sensor_log = {}
    seconds = kb_common.THERMO_RECORD_DELTA_SECONDS
    self._record_interval = datetime.timedelta(seconds=seconds)

  @EventHandler(kbevent.HeartbeatMinuteEvent)
  def _HandleHeartbeat(self, event):
    MAX_AGE = datetime.timedelta(minutes=2)
    now = datetime.datetime.now()
    for sensor_name in self._sensor_log.keys():
      last_update = self._sensor_log[sensor_name]
      if (now - last_update) > MAX_AGE:
        self._logger.warning('Stopped receiving updates for thermo sensor %s' %
            sensor_name)
        del self._sensor_log[sensor_name]

  @EventHandler(kbevent.ThermoEvent)
  def _HandleThermoUpdateEvent(self, event):
    sensor_name = event.sensor_name
    sensor_value = event.sensor_value
    now = datetime.datetime.now()

    # Round down to nearest minute.
    now = now.replace(second=0, microsecond=0)

    # If we've already posted a recording for this minute, avoid doing so again.
    # Note: the backend may also be performing this check.
    last_record = self._name_to_last_record.get(sensor_name)
    if last_record:
      last_time = last_record.record_time
      if last_time == now:
        self._logger.debug('Dropping excessive temp event')
        return

    # If the temperature is out of bounds, reject it.
    # Note: the backend may also be performing this check.
    min_val = kb_common.THERMO_SENSOR_RANGE[0]
    max_val = kb_common.THERMO_SENSOR_RANGE[1]
    if sensor_value < min_val or sensor_value > max_val:
      return

    log_message = 'Recording temperature sensor=%s value=%s' % (sensor_name,
        sensor_value)

    if sensor_name not in self._sensor_log:
      self._logger.info(log_message)
      self._logger.info('Additional readings will only be shown with --verbose')
    else:
      self._logger.debug(log_message)
    self._sensor_log[sensor_name] = now

    try:
      new_record = self._backend.LogSensorReading(sensor_name, sensor_value, now)
      self._name_to_last_record[sensor_name] = new_record
    except ValueError:
      # Value was rejected by the backend; ignore.
      pass

class TokenRecord:
  STATUS_ACTIVE = 'active'
  STATUS_REMOVED = 'removed'

  def __init__(self, auth_device, token_value, tap_name):
    self.auth_device = auth_device
    self.token_value = token_value
    self.tap_name = tap_name
    self.last_seen = datetime.datetime.now()
    self.status = self.STATUS_ACTIVE

  def __str__(self):
    return '%s=%s@%s' % self.AsTuple()

  def AsTuple(self):
    return (self.auth_device, self.token_value, self.tap_name)

  def SetStatus(self, status):
    self.status = status

  def UpdateLastSeen(self):
    self.SetStatus(self.STATUS_ACTIVE)
    self.last_seen = datetime.datetime.now()

  def IdleTime(self):
    return datetime.datetime.now() - self.last_seen

  def IsPresent(self):
    return self.status == self.STATUS_ACTIVE

  def IsRemoved(self):
    return self.status == self.STATUS_REMOVED

  def __hash__(self):
    return hash((self.AsTuple(), other.AsTuple()))

  def __cmp__(self, other):
    if not other:
      return -1
    return cmp(self.AsTuple(), other.AsTuple())


class AuthenticationManager(Manager):
  def __init__(self, name, event_hub, flow_manager, tap_manager, backend):
    Manager.__init__(self, name, event_hub)
    self._flow_manager = flow_manager
    self._tap_manager = tap_manager
    self._backend = backend
    self._tokens = {}  # maps tap name to currently active token
    self._lock = threading.RLock()

  @EventHandler(kbevent.TokenAuthEvent)
  def HandleAuthTokenEvent(self, event):
    for tap in self._GetTapsForTapName(event.tap_name):
      record = self._GetRecord(event.auth_device_name, event.token_value,
          tap.GetName())
      if event.status == event.TokenState.ADDED:
        self._TokenAdded(record)
      else:
        self._TokenRemoved(record)

  def _GetRecord(self, auth_device, token_value, tap_name):
    new_rec = TokenRecord(auth_device, token_value, tap_name)
    existing = self._tokens.get(tap_name)
    if new_rec == existing:
      return existing
    return new_rec

  def _MaybeStartFlow(self, record):
    """Called when the given token has been added.

    This will either start or renew a flow on the FlowManager."""
    username = None
    tap_name = record.tap_name
    try:
      token = self._backend.GetAuthToken(record.auth_device, record.token_value)
      username = token.username
    except backend.NoTokenError:
      pass

    if not username:
      self._logger.info('Token not assigned: %s' % record)
      return

    max_idle = kb_common.AUTH_DEVICE_MAX_IDLE_SECS.get(record.auth_device)
    if max_idle is None:
      max_idle = kb_common.AUTH_DEVICE_MAX_IDLE_SECS['default']
    self._flow_manager.StartFlow(tap_name, username=username,
        max_idle_secs=max_idle)

  def _MaybeEndFlow(self, record):
    """Called when the given token has been removed.

    If the auth device is a captive auth device, then this will forcibly end the
    flow.  Otherwise, this is a no-op."""
    is_captive = kb_common.AUTH_DEVICE_CAPTIVE.get(record.auth_device)
    if is_captive is None:
      is_captive = kb_common.AUTH_DEVICE_CAPTIVE['default']
    if is_captive:
      self._logger.debug('Captive auth device, ending flow immediately.')
      self._flow_manager.StopFlow(record.tap_name)
    else:
      self._logger.debug('Non-captive auth device, not ending flow.')

  @util.synchronized
  def _TokenAdded(self, record):
    """Processes a record when a token is added."""
    self._logger.info('Token attached: %s' % record)
    existing = self._tokens.get(record.tap_name)

    if existing == record:
      # Token is already known; nothing to do except update it.
      record.UpdateLastSeen()
      return

    if existing:
      self._logger.info('Removing previous token')
      self._TokenRemoved(existing)

    self._tokens[record.tap_name] = record
    self._MaybeStartFlow(record)

  @util.synchronized
  def _TokenRemoved(self, record):
    self._logger.info('Token detached: %s' % record)
    if record != self._tokens.get(record.tap_name):
      self._logger.warning('Token has already been removed')
      return

    record.SetStatus(record.STATUS_REMOVED)
    del self._tokens[record.tap_name]
    self._MaybeEndFlow(record)

  def _GetTapsForTapName(self, tap_name):
    if tap_name == kb_common.ALIAS_ALL_TAPS:
      return self._tap_manager.GetAllTaps()
    else:
      if self._tap_manager.TapExists(tap_name):
        return [self._tap_manager.GetTap(tap_name)]
      else:
        return []


class SubscriptionManager(Manager):
  def __init__(self, name, event_hub, server):
    Manager.__init__(self, name, event_hub)
    self._server = server
  @EventHandler(kbevent.CreditAddedEvent)
  @EventHandler(kbevent.DrinkCreatedEvent)
  @EventHandler(kbevent.FlowUpdate)
  @EventHandler(kbevent.SetRelayOutputEvent)
  def RepostEvent(self, event):
    self._server.SendEventToClients(event)
