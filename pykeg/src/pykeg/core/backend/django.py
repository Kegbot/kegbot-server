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

"""Django ORM implementation of backend."""

import datetime
import logging

from . import backend
from pykeg.core import kb_common
from pykeg.core import models
from pykeg.web import tasks
from pykeg.proto import protolib

class KegbotBackend(backend.Backend):
  """Django models backed Backend."""

  def __init__(self, sitename='default', site=None):
    self._logger = logging.getLogger('backend')
    if site:
      self._site = site
    else:
      self._site = models.KegbotSite.objects.get(name=sitename)

  def _GetTapFromName(self, tap_name):
    try:
      return models.KegTap.objects.get(site=self._site, meter_name=tap_name)
    except models.KegTap.DoesNotExist:
      return None

  def _GetKegForTapName(self, tap_name):
    tap = self._GetTapFromName(tap_name)
    if tap and tap.current_keg and tap.current_keg.status == 'online':
      return tap.current_keg
    return None

  def _GetSensorFromName(self, name, autocreate=True):
    try:
      return models.ThermoSensor.objects.get(site=self._site, raw_name=name)
    except models.ThermoSensor.DoesNotExist:
      if autocreate:
        sensor = models.ThermoSensor(site=self._site, raw_name=name, nice_name=name)
        sensor.save()
        return sensor
      else:
        return None

  def _GetUserObjFromUsername(self, username):
    try:
      return models.User.objects.get(username=username)
    except models.User.DoesNotExist:
      return None

  def CreateNewUser(self, username, gender=kb_common.DEFAULT_NEW_USER_GENDER,
      weight=kb_common.DEFAULT_NEW_USER_WEIGHT):
    u = models.User(username=username)
    u.save()
    p = u.get_profile()
    p.gender = gender
    p.weight = weight
    p.save()
    return protolib.ToProto(u)

  def CreateTap(self, name, meter_name, relay_name=None, ml_per_tick=None):
    tap = models.KegTap.objects.create(site=self._site, name=name,
        meter_name=meter_name, relay_name=relay_name, ml_per_tick=ml_per_tick)
    tap.save()
    return protolib.ToProto(tap)

  def CreateAuthToken(self, auth_device, token_value, username=None):
    token = models.AuthenticationToken.objects.create(
        site=self._site, auth_device=auth_device, token_value=token_value)
    if username:
      user = self._GetUserObjFromUsername(username)
      token.user = user
    token.save()
    return protolib.ToProto(token)

  def GetAllTaps(self):
    return protolib.ToProto(list(models.KegTap.objects.all()))

  def RecordDrink(self, tap_name, ticks, volume_ml=None, username=None,
      pour_time=None, duration=0, auth_token=None, spilled=False,
      shout='', do_postprocess=True):

    tap = self._GetTapFromName(tap_name)
    if not tap:
      raise backend.BackendError("Tap unknown")

    if volume_ml is None:
      volume_ml = float(ticks) * tap.ml_per_tick

    user = None
    if username:
      user = self._GetUserObjFromUsername(username)

    if not pour_time:
      pour_time = datetime.datetime.now()

    keg = None
    if tap.current_keg and tap.current_keg.status == 'online':
      keg = tap.current_keg

    if spilled:
      if not keg:
        self._logger.warning('Got spilled pour for tap missing keg; ignoring')
        return
      keg.spilled_ml += volume_ml
      keg.save()
      return

    d = models.Drink(ticks=ticks, site=self._site, keg=keg, user=user,
        volume_ml=volume_ml, starttime=pour_time, duration=duration,
        auth_token=auth_token, shout=shout)
    models.DrinkingSession.AssignSessionForDrink(d)
    d.save()
    if do_postprocess:
      d.PostProcess()
      event_list = [e for e in models.SystemEvent.objects.filter(drink=d).order_by('id')]
      tasks.handle_new_events.delay(self._site, event_list)

    return protolib.ToProto(d)

  def CancelDrink(self, seqn, spilled=False):
    try:
      d = self._site.drinks.get(seqn=seqn)
    except models.Drink.DoesNotExist:
      return

    keg = d.keg
    user = d.user
    session = d.session

    # Transfer volume to spillage if requested.
    if spilled and d.volume_ml and d.keg:
      d.keg.spilled_ml += d.volume_ml
      d.keg.save()

    d.status = 'deleted'
    d.save()

    # Invalidate all statistics.
    models.SystemStats.objects.filter(site=self._site).delete()
    models.KegStats.objects.filter(site=self._site, keg=d.keg).delete()
    models.UserStats.objects.filter(site=self._site, user=d.user).delete()
    models.SessionStats.objects.filter(site=self._site, session=d.session).delete()

    # Delete any SystemEvents for this drink.
    models.SystemEvent.objects.filter(site=self._site, drink=d).delete()

    # Regenerate new statistics, based on the most recent drink
    # post-cancellation.
    last_qs = self._site.drinks.valid().order_by('-seqn')
    if last_qs:
      last_drink = last_qs[0]
      last_drink._UpdateSystemStats()

    if keg:
      keg.RecomputeStats()
    if user and user.get_profile():
      user.get_profile().RecomputeStats()
    if session:
      session.Rebuild()
      session.RecomputeStats()

    # TODO(mikey): recompute session.
    return protolib.ToProto(d)

  def LogSensorReading(self, sensor_name, temperature, when=None):
    if not when:
      when = datetime.datetime.now()

    # The maximum resolution of ThermoSensor records is 1 minute.  Round the
    # time down to the nearest minute; if a record already exists for this time,
    # replace it.
    when = when.replace(second=0, microsecond=0)

    # If the temperature is out of bounds, reject it.
    min_val = kb_common.THERMO_SENSOR_RANGE[0]
    max_val = kb_common.THERMO_SENSOR_RANGE[1]
    if temperature < min_val or temperature > max_val:
      raise ValueError('Temperature out of bounds')

    sensor = self._GetSensorFromName(sensor_name)
    defaults = {
        'temp': temperature,
    }
    record, created = models.Thermolog.objects.get_or_create(site=self._site,
        sensor=sensor, time=when, defaults=defaults)
    record.temp = temperature
    record.save()
    return protolib.ToProto(record)

  def GetAuthToken(self, auth_device, token_value):
    # Special case for "core.user" psuedo auth device.
    if auth_device == 'core.user':
      try:
        user = models.User.objects.get(username=token_value, is_active=True)
      except models.User.DoesNotExist:
        raise backend.NoTokenError(auth_device)
      fake_token = models.AuthenticationToken(auth_device='core.user',
          token_value=token_value, seqn=0, user=user, enabled=True)
      return protolib.ToProto(fake_token)

    if token_value and auth_device in kb_common.AUTH_MODULE_NAMES_HEX_VALUES:
      token_value = token_value.lower()
    tok, created = models.AuthenticationToken.objects.get_or_create(site=self._site,
        auth_device=auth_device, token_value=token_value)
    if not tok.user:
      raise backend.NoTokenError
    return protolib.ToProto(tok)

