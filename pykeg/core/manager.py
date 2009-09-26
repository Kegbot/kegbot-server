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

"""Tap (single path of fluid) management module."""

import datetime
import inspect
import logging

from pykeg.core import event
from pykeg.core import flow_meter
from pykeg.core import kb_common
from pykeg.core import models
from pykeg.core import units
from pykeg.core.net import kegnet_message

KB_EVENT = kb_common.KB_EVENT


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


class Manager(object):
  def __init__(self, name, kb_env):
    self._name = name
    self._kb_env = kb_env
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

  def _PublishEvent(self, event, payload=None):
    """Convenience alias for EventHub.PublishEvent"""
    self._kb_env.GetEventHub().PublishEvent(event, payload)


class Tap(object):
  def __init__(self, name, ml_per_tick):
    self._name = name
    self._ml_per_tick = ml_per_tick
    self._meter = flow_meter.FlowMeter(name)

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

  def __init__(self, name, kb_env):
    Manager.__init__(self, name, kb_env)
    self._taps = {}
    all_taps = models.KegTap.objects.all()
    for tap in all_taps:
      self.RegisterTap(tap.meter_name, tap.ml_per_tick)

  def TapExists(self, name):
    return name in self._taps

  def GetAllTaps(self):
    return self._taps.values()

  def _CheckTapExists(self, name):
    if not self.TapExists(name):
      raise UnknownTapError

  def RegisterTap(self, name, ml_per_tick):
    self._logger.info('Registering new tap: %s' % name)
    if self.TapExists(name):
      raise AlreadyRegisteredError
    self._taps[name] = Tap(name, ml_per_tick)

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
  def __init__(self, tap):
    self._tap = tap
    self._start_time = datetime.datetime.now()
    self._end_time = None
    self._bound_user = None
    self._last_log_time = None
    self._total_ticks = 0L

  def __str__(self):
    return '<Flow %s ticks=%s user=%s>' % (self._tap, self._total_ticks,
        self._bound_user)

  def AddTicks(self, amount, when=None):
    self._total_ticks += amount
    if when is None:
      when = datetime.datetime.now()
    if self._start_time is None:
      self._start_time = when
    self._end_time = when

  def GetTicks(self):
    return self._total_ticks

  def GetVolumeMl(self):
    return self._tap.TicksToMilliliters(self._total_ticks)

  def GetUser(self):
    return self._bound_user

  def SetUser(self, user):
    self._bound_user = user

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
  def __init__(self, name, kb_env):
    Manager.__init__(self, name, kb_env)
    self._flow_map = {}
    self._logger = logging.getLogger("flowmanager")

  def GetActiveFlows(self):
    return self._flow_map.values()

  def GetFlow(self, tap_name):
    return self._flow_map.get(tap_name)

  def StartFlow(self, tap_name):
    if not self.GetFlow(tap_name):
      tap_manager = self._kb_env.GetTapManager()
      tap = tap_manager.GetTap(tap_name)
      new_flow = Flow(tap)
      self._flow_map[tap_name] = new_flow
      self._logger.info('StartFlow: Flow created: %s' % new_flow)
    else:
      self._logger.info('StartFlow: Flow already exists on %s' % tap_name)
    return self.GetFlow(tap_name)

  def EndFlow(self, tap_name):
    flow = self.GetFlow(tap_name)
    if flow:
      tap = flow.GetTap()
      del self._flow_map[tap_name]
      self._logger.info('EndFlow: Flow ended: %s' % flow)
    else:
      self._logger.info('EndFlow: No existing flow on tap %s' % (tap_name,))
    return flow

  def UpdateFlow(self, tap_name, volume):
    try:
      tap_manager = self._kb_env.GetTapManager()
      tap = tap_manager.GetTap(tap_name)
    except TapManagerError:
      # tap is unknown or not available
      # TODO(mikey): guard against this happening
      return None, None

    delta = tap_manager.UpdateDeviceReading(tap.GetName(), volume)
    self._logger.debug('Flow update: tap=%s volume=%i (delta=%i)' %
        (tap_name, volume, delta))

    if delta == 0:
      return None, None

    is_new = False
    flow = self.GetFlow(tap_name)
    if flow is None:
      self._logger.debug('Starting flow implicitly due to activity.')
      flow = self.StartFlow(tap_name)
      is_new = True
    flow.AddTicks(delta, datetime.datetime.now())

    return flow, is_new

  @EventHandler(KB_EVENT.FLOW_DEV_ACTIVITY)
  def HandleFlowActivityEvent(self, ev):
    """Handles the FLOW_DEV_ACTIVITY event.

    The handler accquires the FlowManager, and calls FlowUpdate.  This may
    result in one of three outcomes:
      - New flow created. A FLOW_START event is emitted, followed by a
        FLOW_UPDATE event.
      - Existing flow updated. A FLOW_UPDATE event is emitted.
      - Update refused.  The channel is unknown by the FlowManager.  No events
        are emitted.
    """
    msg = ev.payload
    tap_mgr = self._kb_env.GetTapManager()
    if not tap_mgr.TapExists(msg.tap_name):
      self._logger.warning('Dropping flow update event for unknown tap: %s' %
          (msg.tap_name,))
      return
    flow_instance, is_new = self.UpdateFlow(msg.tap_name, msg.meter_reading)

  @EventHandler(KB_EVENT.FLOW_DEV_IDLE)
  def HandleFlowIdleEvent(self, ev):
    flow = self.EndFlow(ev.payload.tap_name)
    msg = kegnet_message.FlowUpdateMessage.FromFlow(flow)
    self._PublishEvent(KB_EVENT.FLOW_END, msg)

  @EventHandler(KB_EVENT.START_FLOW)
  def _HandleStartFlowEvent(self, ev):
    flow = self.StartFlow(ev.payload.tap_name)
    msg = kegnet_message.FlowUpdateMessage.FromFlow(flow)
    self._PublishEvent(KB_EVENT.FLOW_START, msg)

  @EventHandler(KB_EVENT.END_FLOW)
  def _HandleFlowEndFlowEvent(self, ev):
    flow = self.EndFlow(ev.payload.tap_name)
    msg = kegnet_message.FlowUpdateMessage.FromFlow(flow)
    self._PublishEvent(KB_EVENT.FLOW_END, msg)

class DrinkManager(Manager):

  @EventHandler(KB_EVENT.FLOW_END)
  def HandleFlowEndedEvent(self, ev):
    """Attempt to save a drink record and derived data for |flow|"""
    self._logger.info('Flow completed')
    flow_update = ev.payload

    ticks = flow_update.ticks
    volume_ml = flow_update.volume_ml

    if volume_ml <= kb_common.MIN_VOLUME_TO_RECORD:
      self._logger.info('Not recording flow: volume (%i mL) <= '
        'MIN_VOLUME_TO_RECORD (%i)' % (volume_ml, kb_common.MIN_VOLUME_TO_RECORD))
      return

    keg = None
    try:
      tap = models.KegTap.objects.get(meter_name=flow_update.tap_name)
      if tap.current_keg:
        keg = tap.current_keg
        self._logger.info('Binding drink to keg: %s' % keg)
    except models.KegTap.DoesNotExist:
      self._logger.warning('No tap found for meter %s' % flow_update.tap_name)

    try:
      user = models.User.objects.get(username=flow_update.user)
    except models.User.DoesNotExist:
      user = self._kb_env.GetBackend().GetDefaultUser()
      self._logger.info('User unknown, using default: %s' % (user.username,))

    # log the drink
    d = models.Drink(ticks=int(ticks),
                     volume_ml=volume_ml,
                     starttime=flow_update.start_time,
                     endtime=flow_update.end_time,
                     user=user,
                     keg=keg,
                     status='valid')
    d.save()

    keg_id = None
    if d.keg:
      keg_id = d.keg.id

    self._logger.info('Logged drink %i user=%s keg=%s ounces=%s ticks=%i' % (
      d.id, d.user.username, keg_id, d.Volume().ConvertTo.Ounce,
      d.ticks))

    # notify listeners
    msg = kegnet_message.DrinkCreatedMessage.FromFlowAndDrink(flow_update, d)
    self._PublishEvent(KB_EVENT.DRINK_CREATED, msg)

  @EventHandler(KB_EVENT.DRINK_CREATED)
  def HandleDrinkCreatedEvent(self, ev):
    drink = models.Drink.objects.get(id=ev.payload.drink_id)

    models.BAC.ProcessDrink(drink)
    self._logger.info('Processed BAC for drink %i' % (drink.id,))

    models.UserDrinkingSessionAssignment.RecordDrink(drink)
    self._logger.info('Processed UserDrinkGroupAssignment for drink %i' % (drink.id,))


class ThermoManager(Manager):
  def __init__(self, name, kb_env):
    Manager.__init__(self, name, kb_env)
    self._last_record = {}
    self._same_value_min_delta = datetime.timedelta(minutes=1)
    self._new_value_min_delta = datetime.timedelta(seconds=30)

  @EventHandler(KB_EVENT.THERMO_UPDATE)
  def _HandleThermoUpdateEvent(self, ev):
    sensor_name = ev.payload.sensor_name
    sensor_value = ev.payload.sensor_value
    now = datetime.datetime.now()
    last_record = self._last_record.get(sensor_name)

    if last_record is not None:
      delta = now - last_record.time
      is_new_value = sensor_value != last_record.temp

      if is_new_value and (delta < self._new_value_min_delta):
        # New value, but arrived too soon: drop it.
        self._logger.debug('Dropping new sensor reading, value=%s delta=%s' % (sensor_value, delta))
        return
      elif not is_new_value and (delta < self._same_value_min_delta):
        self._logger.debug('Dropping same sensor reading, value=%s delta=%s' % (sensor_value, delta))
        # Unchanged value, but arrived too soon: drop it.
        return

    self._logger.debug('Recording sensor reading, value=%s' % (sensor_value,))
    new_record = models.Thermolog(name=sensor_name, temp=sensor_value, time=now)
    new_record.save()
    self._last_record[sensor_name] = new_record

class TimeoutCache:
  def __init__(self, maxage):
    self._max_delta = maxage
    self._entries = {}

  def present(self, k):
    now = datetime.datetime.now()
    if k in self._entries:
      age = now - self._entries[k]
      if age > self._max_delta:
        self.remove(k)
        return False
      else:
        return True
    return False

  def touch(self, k):
    if k in self._entries:
      self._entries[k] = datetime.datetime.now()

  def remove(self, k):
    del self._entries[k]

  def put(self, k):
    self._entries[k] = datetime.datetime.now()


class AuthenticationManager(Manager):
  def __init__(self, name, kb_env):
    Manager.__init__(self, name, kb_env)
    self._present_tokens = TimeoutCache(datetime.timedelta(seconds=3))

  def _GetTapsForTapName(self, tap_name):
    tap_manager = self._kb_env.GetTapManager()
    if tap_name == kb_common.ALIAS_ALL_TAPS:
      return tap_manager.GetAllTaps()
    else:
      return tap_manager.GetTap(tap_name)

  @EventHandler(KB_EVENT.AUTH_USER_ADDED)
  def HandleAuthUserAddedEvent(self, ev):
    msg = ev.payload
    flow_mgr = self._kb_env.GetFlowManager()
    flow = flow_mgr.StartFlow(msg.tap_name)
    try:
      user = models.User.objects.get(username=msg.user_name)
      flow.SetUser(user)
    except models.User.DoesNotExist:
      pass

  @EventHandler(KB_EVENT.AUTH_USER_REMOVED)
  def HandleAuthUserRemovedEvent(self, ev):
    msg = ev.payload
    flow_mgr = self._kb_env.GetFlowManager()
    flow = flow_mgr.EndFlow(msg.tap_name)

  @EventHandler(KB_EVENT.AUTH_TOKEN_ADDED)
  def HandleAuthTokenAddedEvent(self, ev):
    msg = ev.payload
    tap_name = msg.tap_name
    auth_device_name = msg.auth_device_name
    token_value = msg.token_value.lower()
    token_pair = (auth_device_name, token_value)

    if self._present_tokens.present(token_pair):
      # we already know about this token; process no further
      self._present_tokens.touch(token_pair)
      return
    else:
      self._present_tokens.put(token_pair)

    try:
      token = models.AuthenticationToken.objects.get(auth_device=auth_device_name,
          token_value=token_value)
    except models.AuthenticationToken.DoesNotExist:
      self._logger.info('Token does not exist: %s.%s' % (auth_device_name, token_value))
      return

    if not token.user:
      self._logger.info('Token not assigned.')
      return

    # TODO(mikey): should virtual taps (__all_taps__) be handled elsewhere?
    for tap in self._GetTapsForTapName(tap_name):
      message = kegnet_message.AuthUserAddMessage(tap_name=tap.GetName(),
          user_name=token.user.username)

    self._PublishEvent(KB_EVENT.AUTH_USER_ADDED, message)
