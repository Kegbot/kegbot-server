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

from pykeg.core import flow_meter
from pykeg.core import kb_common
from pykeg.core import util
from pykeg.core.net import kegnet_pb2

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

  def GetStatus(self):
    return []

  def _PublishEvent(self, event):
    """Convenience alias for EventHub.PublishEvent"""
    self._event_hub.PublishEvent(event)


class Tap:
  def __init__(self, name, ml_per_tick, max_tick_delta):
    self._name = name
    self._ml_per_tick = ml_per_tick
    self._meter = flow_meter.FlowMeter(name, max_delta=max_tick_delta)

  def __str__(self):
    return self._name

  def GetName(self):
    return self._name

  def GetMeter(self):
    return self._meter

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

  def GetStatus(self):
    ret = []
    for tap in self.GetAllTaps():
      meter = tap.GetMeter()
      ret.append('Tap "%s"' % tap.GetName())
      ret.append('  last activity: %s' % (meter.GetLastActivity(),))
      ret.append('   last reading: %s' % (meter.GetLastReading(),))
      ret.append('    total ticks: %s' % (meter.GetTicks(),))
      ret.append('')

  def TapExists(self, name):
    return name in self._taps

  def GetAllTaps(self):
    return self._taps.values()

  def _CheckTapExists(self, name):
    if not self.TapExists(name):
      raise UnknownTapError

  def RegisterTap(self, name, ml_per_tick, max_tick_delta):
    self._logger.info('Registering new tap: %s' % name)
    if self.TapExists(name):
      raise AlreadyRegisteredError
    self._taps[name] = Tap(name, ml_per_tick, max_tick_delta)

  def UnregisterTap(self, name):
    self._logger.info('Unregistering tap: %s' % name)
    self._CheckTapExists(name)
    del self._taps[name]

  def GetTap(self, name):
    self._CheckTapExists(name)
    return self._taps[name]

  def UpdateDeviceReading(self, name, value):
    meter = self.GetTap(name).GetMeter()
    delta = meter.SetTicks(value)
    return delta


class Flow:
  def __init__(self, tap, flow_id, username=None):
    self._tap = tap
    self._flow_id = flow_id
    self._bound_username = username
    self._state = kegnet_pb2.FlowUpdate.INITIAL
    self._start_time = datetime.datetime.now()
    self._end_time = None
    self._last_log_time = None
    self._total_ticks = 0L

  def __str__(self):
    return '<Flow %s ticks=%s username=%s>' % (self._tap, self._total_ticks,
        self._bound_username)

  def GetUpdateEvent(self):
    event = kegnet_pb2.FlowUpdate()
    event.flow_id = self._flow_id
    event.tap_name = self._tap.GetName()
    event.state = self._state

    # TODO(mikey): username or user_name in the proto, not both
    if self._bound_username:
      event.username = self._bound_username

    event.start_time = int(time.mktime(self._start_time.timetuple()))
    end = self._start_time
    if self._end_time:
      end = self._end_time
    event.last_activity_time = int(time.mktime(end.timetuple()))
    event.ticks = self.GetTicks()
    event.volume_ml = self.GetVolumeMl()

    return event

  def AddTicks(self, amount, when=None):
    self._total_ticks += amount
    if when is None:
      when = datetime.datetime.now()
    if self._start_time is None:
      self._start_time = when
    self._end_time = when

  def GetId(self):
    return self._flow_id

  def GetState(self):
    return self._state

  def SetState(self, state):
    self._state = state

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
    if end_time is None:
      return datetime.timedelta(0)
    return datetime.datetime.now() - end_time

  def GetTap(self):
    return self._tap


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

  def GetStatus(self):
    ret = []
    active_flows = self.GetActiveFlows()
    if not active_flows:
      ret.append('Active flows: None')
    else:
      ret.append('Active flows: %i' % len(active_flows))
      for flow in active_flows:
        ret.append('  Flow on tap %s' % flow.GetTap())
        ret.append('         username: %s' % flow.GetUsername())
        ret.append('            ticks: %i' % flow.GetTicks())
        ret.append('      volume (mL): %i' % flow.GetVolumeMl())
        ret.append('       start time: %s' % flow.GetStartTime())
        ret.append('      last active: %s' % flow.GetEndTime())
        ret.append('')

    return ret

  def GetActiveFlows(self):
    return self._flow_map.values()

  def GetFlow(self, tap_name):
    return self._flow_map.get(tap_name)

  def StartFlow(self, tap_name, username=''):
    try:
      if not self.GetFlow(tap_name):
        tap = self._tap_manager.GetTap(tap_name)
        #if user is None:
        #  users = self._auth_manager.GetActiveUsers()
        #  if users:
        #    user = list(users)[0]
        new_flow = Flow(tap, self._GetNextFlowId(), username)
        self._flow_map[tap_name] = new_flow
        self._logger.info('StartFlow: Flow created: %s' % new_flow)
        self._PublishUpdate(new_flow)
      else:
        self._logger.info('StartFlow: Flow already exists on %s' % tap_name)
      return self.GetFlow(tap_name)
    except UnknownTapError:
      return None

  def SetUsername(self, flow, username):
    flow.SetUsername(username)
    self._PublishUpdate(flow)

  def EndFlow(self, tap_name):
    self._logger.info('Ending flow on tap %s' % tap_name)
    try:
      flow = self.GetFlow(tap_name)
      if flow:
        tap = flow.GetTap()
        del self._flow_map[tap_name]
        self._logger.info('EndFlow: Flow ended: %s' % flow)
        self._StateChange(flow, kegnet_pb2.FlowUpdate.COMPLETED)
      else:
        self._logger.info('EndFlow: No existing flow on tap %s' % (tap_name,))
      return flow
    except UnknownTapError:
      return None

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

    if flow.GetState() != kegnet_pb2.FlowUpdate.ACTIVE:
      self._StateChange(flow, kegnet_pb2.FlowUpdate.ACTIVE)
    else:
      self._PublishUpdate(flow)

    return flow, is_new

  def _StateChange(self, flow, new_state):
    flow.SetState(new_state)
    self._PublishUpdate(flow)

  def _PublishUpdate(self, flow):
    event = flow.GetUpdateEvent()
    self._PublishEvent(event)

  @EventHandler(kegnet_pb2.MeterUpdate)
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

  @EventHandler(kegnet_pb2.HeartbeatSecondEvent)
  def _HandleHeartbeatEvent(self, event):
    # TODO(mikey): Allowable idle time must be configurable.
    max_idle = datetime.timedelta(seconds=10)
    for flow in self.GetActiveFlows():
      idle_time = flow.GetIdleTime()
      if idle_time > max_idle:
        self._logger.info('Flow has become too idle, ending: %s' % flow)
        self._StateChange(flow, kegnet_pb2.FlowUpdate.IDLE)
        self.EndFlow(flow.GetTap().GetName())

  @EventHandler(kegnet_pb2.FlowRequest)
  def _HandleFlowRequestEvent(self, event):
    if event.request == event.START_FLOW:
      self.StartFlow(event.tap_name)
    elif event.request == event.STOP_FLOW:
      self.EndFlow(event.tap_name)


class DrinkManager(Manager):
  def __init__(self, name, event_hub, backend):
    Manager.__init__(self, name, event_hub)
    self._backend = backend
    self._last_drink = None

  def GetStatus(self):
    ret = []
    ret.append('Last drink: %s' % self._last_drink)
    return ret

  @EventHandler(kegnet_pb2.FlowUpdate)
  def HandleFlowUpdateEvent(self, event):
    """Attempt to save a drink record and derived data for |flow|"""
    if event.state == event.COMPLETED:
      self._HandleFlowEnded(event)

  def _HandleFlowEnded(self, event):
    self._logger.info('Flow completed for flow_id=%i' % event.flow_id)

    ticks = event.ticks
    username = event.username
    volume_ml = event.volume_ml
    tap_name = event.tap_name
    starttime = datetime.datetime.fromtimestamp(event.start_time)
    pour_time = datetime.datetime.fromtimestamp(event.last_activity_time)
    duration = (pour_time - starttime).seconds
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
        pour_time=pour_time, duration=duration, auth_token=auth_token)

    keg_id = None
    if d.keg:
      keg_id = d.keg.id

    username = '<None>'
    if d.user_id:
      username = d.user_id
    self._logger.info('Logged drink %i username=%s keg=%s liters=%.2f ticks=%i' % (
      d.id, username, keg_id, d.volume_ml/1000.0, d.ticks))

    self._last_drink = d

    # notify listeners
    created = kegnet_pb2.DrinkCreatedEvent()
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
    seconds = kb_common.THERMO_RECORD_DELTA_SECONDS
    self._record_interval = datetime.timedelta(seconds=seconds)

  def GetStatus(self):
    ret = []
    if not self._name_to_last_record:
      ret.append('No readings.')
      return ret
    ret.append('Last recorded temperature(s):')
    for sensor, value in self._name_to_last_record.iteritems():
      ret.append('  %s: %.2f' % (sensor, value))
    return ret

  @EventHandler(kegnet_pb2.ThermoEvent)
  def _HandleThermoUpdateEvent(self, event):
    sensor_name = event.sensor_name
    sensor_value = event.sensor_value
    now = datetime.datetime.now()

    # If we've already posted a recording for this minute, avoid doing so again.
    last_record = self._name_to_last_record.get(sensor_name)
    if last_record:
      last_time = datetime.datetime.fromtimestamp(last_record.record_time)
      if last_time.timetuple()[:5] == now.timetuple()[:5]:
        self._logger.debug('Dropping excessive temp event')
        return

    # If the temperature is out of bounds, reject it.
    min_val = kb_common.THERMO_SENSOR_RANGE[0]
    max_val = kb_common.THERMO_SENSOR_RANGE[1]
    if sensor_value < min_val or sensor_value > max_val:
      return

    self._logger.info('Recording temperature sensor=%s value=%s' %
                      (sensor_name, sensor_value))

    try:
      new_record = self._backend.LogSensorReading(sensor_name, sensor_value, now)
      self._name_to_last_record[sensor_name] = new_record
    except ValueError:
      # Value was out of acceptable range; ignore.
      pass

class TokenRecord:
  STATUS_ACTIVE = 1
  STATUS_REMOVED = 2

  def __init__(self, auth_device, token_value, tap_name):
    self.auth_device = auth_device
    self.token_value = token_value
    self.tap_name = tap_name
    self.last_seen = datetime.datetime.now()
    self.status = self.STATUS_ACTIVE

  def __str__(self):
    return str(self.AsTuple())

  def AsTuple(self):
    return (self.auth_device, self.token_value, self.tap_name)

  def SetStatus(self, status):
    self.status = status

  def UpdateLastSeen(self):
    self.SetStatus(self.STATUS_ACTIVE)
    self.last_seen = datetime.datetime.now()

  def IdleTime(self):
    return datetime.datetime.now() - self.last_seen

  def MaxIdleTime(self):
    amt = kb_common.AUTH_TOKEN_MAX_IDLE.get(self.auth_device, 0)
    return datetime.timedelta(seconds=amt)

  def IsIdle(self):
    if self.status == self.STATUS_REMOVED:
      return self.IdleTime() >= self.MaxIdleTime()
    else:
      return False

  def __hash__(self):
    return hash((self.AsTuple(), other.AsTuple()))

  def __cmp__(self, other):
    if not other:
      return -1
    return cmp(self.AsTuple(), other.AsTuple())


class TokenManager(Manager):
  """Keeps track of tokens arriving and departing from taps.

  Token events have four components:
    * the name of the tap on which the event is being reported;
    * the name of the authentication device generating the event;
    * the value of the token being reported, an opaque key;
    * the sense of the event, whether the token was added or removed.

  The TokenManager is responsible for generating UserAuthEvents as a result of
  token events.  It is the primary (but not necessarily only) source of
  authorization events.

  If the token was added, the TokenManager should attempt to associate it with a
  user, and generate a UserAuthEvent if valid.  If the token was detached, the
  TokenManager will wait for a timeout (possibly zero) before considering the
  token 'removed'.  If the token re-appears during this time, it is as if the
  token was never removed.  Otherwise, the TokenManager issues a UserAuthEvent
  de-authorizing the user.
  """
  def __init__(self, name, event_hub, backend):
    Manager.__init__(self, name, event_hub)
    self._backend = backend
    self._tokens = {}  # maps tap name to currently active token
    self._lock = threading.Lock()

  @EventHandler(kegnet_pb2.TokenAuthEvent)
  def HandleAuthTokenEvent(self, event):
    if event.status == event.ADDED:
      self._TokenAdded(event)
    else:
      self._TokenRemoved(event)

  @EventHandler(kegnet_pb2.HeartbeatSecondEvent)
  def HandleHeartbeatEvent(self, event):
    for tap_name, record in self._tokens.items():
      if record.IsIdle():
        self._logger.info('Token has been removed: %s' % record)
        self._RemoveRecord(record)

  def _GetRecordFromEvent(self, event):
    auth_device = event.auth_device_name
    token_value = event.token_value
    tap_name = event.tap_name

    new_rec = TokenRecord(auth_device, token_value, tap_name)
    existing = self._tokens.get(event.tap_name)

    if new_rec == existing:
      return existing

    return new_rec

  def _PublishAuthEvent(self, record, added):
    user = None
    token = self._backend.GetAuthToken(record.auth_device, record.token_value)

    if not token or not token.user:
      self._logger.info('Token not assigned: %s' % record)
      return

    user_name = token.user.username

    message = kegnet_pb2.UserAuthEvent()
    message.tap_name = record.tap_name
    message.user_name = user_name
    if added:
      message.state = message.ADDED
    else:
      message.state = message.REMOVED
    self._PublishEvent(message)

  def _TokenRemoved(self, event):
    record = self._GetRecordFromEvent(event)
    self._logger.info('Token removed: %s' % record)

    if self._tokens.get(record.tap_name) != record:
      return

    # Depending on the authentication device token timeout, either remove the
    # token immediately, or just wait for it to be idled out.
    record.SetStatus(record.STATUS_REMOVED)
    timeout = record.MaxIdleTime()
    if not timeout:
      self._logger.info('Immediately removing token %s' % record)
      self._RemoveRecord(record)

  @util.synchronized
  def _RemoveRecord(self, record):
    record.SetStatus(record.STATUS_REMOVED)
    del self._tokens[record.tap_name]
    self._logger.info('Removing record %s' % record)
    self._PublishAuthEvent(record, False)

  def _ActiveRecordForTap(self, tap_name):
    return self._tokens.get(tap_name)

  def _TokenAdded(self, event):
    """Processes a TokenAuthEvent when a token is added."""
    existing = self._ActiveRecordForTap(event.tap_name)
    record = self._GetRecordFromEvent(event)
    self._logger.info('Token attached: %s' % record)

    if existing == record:
      # Token is already known; nothing to do except update it.
      record.UpdateLastSeen()
      return

    if existing:
      self._logger.info('Detaching previous token: %s' % existing)
      self._RemoveRecord(existing)

    self._tokens[record.tap_name] = record
    self._PublishAuthEvent(record, True)


class AuthenticationManager(Manager):
  def __init__(self, name, event_hub, flow_manager, tap_manager, backend):
    Manager.__init__(self, name, event_hub)
    self._flow_manager = flow_manager
    self._tap_manager = tap_manager
    self._backend = backend
    self._users_by_tap = {}

  def _AddUser(self, username, tap):
    tap_name = tap.GetName()
    old_user = self._users_by_tap.get(tap_name)
    if old_user:
      if old_user == username:
        self._logger.info('User %s@%s already authenticated' % (username, tap_name))
        return
      else:
        self._logger.info('New user "%s" authenticated on tap %s, kicking old user "%s"' %
            (username, tap_name, old_user))
        self._RemoveUser(tap)
    self._users_by_tap[tap_name] = username
    self._logger.info('Authenticated user %s@%s' % (username, tap_name))

    # Ask the flow manager to start a flow for this user & tap.
    # TODO(mikey): FlowManager should do this as the result of an authentication
    # event.
    flow = self._flow_manager.GetFlow(tap.GetName())
    if flow is None:
      self._flow_manager.StartFlow(tap.GetName(), username)
    else:
      self._flow_manager.SetUser(flow, username)

  def _RemoveUser(self, tap):
    tap_name = tap.GetName()
    username = self._users_by_tap.get(tap_name)
    if not username:
      self._logger.warning('No user authenticated on tap %s' % tap_name)
      return
    del self._users_by_tap[tap_name]
    self._logger.info('Deauthenticated user %s@%s' % (username, tap_name))

    # Ask the flow manager to stop a flow on this tap.
    # TODO(mikey): FlowManager should do this as the result of an authentication
    # event.
    self._flow_manager.EndFlow(tap.GetName())

  @EventHandler(kegnet_pb2.UserAuthEvent)
  def HandleUserAuthEvent(self, event):
    username = event.user_name
    if not username:
      self._logger.warning('Ignoring auth event for unknown username.')
      return

    taps = self._GetTapsForTapName(event.tap_name)
    if not taps:
      self._logger.warning('Ignoring auth event for unknown tap %s' %
          event.tap_name)
      return

    for tap in taps:
      if event.state == event.ADDED:
        self._AddUser(username, tap)
      else:
        self._RemoveUser(tap)

  def GetActiveUsers(self):
    return set(self._users_by_tap.values())

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
  @EventHandler(kegnet_pb2.CreditAddedEvent)
  @EventHandler(kegnet_pb2.DrinkCreatedEvent)
  @EventHandler(kegnet_pb2.FlowUpdate)
  def RepostEvent(self, event):
    self._server.SendEventToClients(event)
