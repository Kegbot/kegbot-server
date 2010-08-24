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

"""Wrapper module for database implementation."""

import logging

from django.db.utils import DatabaseError

from pykeg.core import kb_common
from pykeg.core import config
from pykeg.core import models
from pykeg.core import protolib

class BackendError(Exception):
  """Base backend error exception."""

class Backend:
  """Abstract base Kegbot backend class.

  This class defines the interface that pykeg uses to talk to the kegbot
  backend.
  """

  def GetConfig(self):
    """Returns a KegbotConfig instance based on the current database values."""
    raise NotImplementedError

  def GetUserFromUsername(self, username):
    """Returns the User matching the given username, or None."""
    raise NotImplementedError

  def CreateNewUser(self, username, gender=kb_common.DEFAULT_NEW_USER_GENDER,
      weight=kb_common.DEFAULT_NEW_USER_WEIGHT):
    """Creates a new User instance.

    Args
      username: the unique username for the new User
      gender: the gender to assign the new user
      weight: the weight to assign the new user
    Returns
      the new User instance
    """
    raise NotImplementedError

  def GetAllTaps(self):
    """Returns all currently enabled taps."""
    raise NotImplementedError

  def RecordDrink(self, ticks, volume_ml, starttime, endtime, user, keg=None,
      status='valid'):
    """Records a new drink with the given parameters."""
    raise NotImplementedError

  def LogSensorReading(self, sensor_name, temperature, when):
    """Records a new sensor reading."""
    raise NotImplementedError

  def GetAuthToken(self, auth_device, token_value):
    """Returns an AuthenticationToken instance."""
    raise NotImplementedError


class KegbotBackend(Backend):
  """Django models backed Backend."""

  def __init__(self, sitename='default'):
    self._logger = logging.getLogger('backend')
    self._config = config.KegbotConfig(self._GetConfigDict())
    self._site = models.KegbotSite.objects.get(name=sitename)

  def _GetConfigDict(self):
    try:
      ret = {}
      for row in models.Config.objects.all():
        ret[row.key] = row.value
      return ret
    except DatabaseError, e:
      raise BackendError, e

  def _GetKegForTap(self, tap_name):
    try:
      tap = models.KegTap.objects.get(site=self._site, meter_name=tap_name)
      if tap.current_keg and tap.current_keg.status == 'online':
        return tap.current_keg
    except models.KegTap.DoesNotExist:
      pass
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

  def GetConfig(self):
    return self._config

  def GetUserFromUsername(self, username):
    return protolib.ToProto(self._GetUserObjFromUsername(username))

  def CreateNewUser(self, username, gender=kb_common.DEFAULT_NEW_USER_GENDER,
      weight=kb_common.DEFAULT_NEW_USER_WEIGHT):
    u = models.User(username=username)
    u.save()
    p = u.get_profile()
    p.gender = gender
    p.weight = weight
    p.save()
    return protolib.ToProto(u)

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

  def RecordDrink(self, ticks, volume_ml, starttime, endtime, username=None,
      tap_name=None, status='valid'):

    # Look up the username, selecting the default user if unknown/invalid.
    user = self._GetUserObjFromUsername(username)

    # Look up the tap name, assigning the current keg on the tap if valid.
    keg = None
    if tap_name:
      keg = self._GetKegForTap(tap_name)

    d = models.Drink(site=self._site, ticks=int(ticks), volume_ml=volume_ml,
        starttime=starttime, endtime=endtime, user=user, keg=keg, status=status)
    d.save()
    return protolib.ToProto(d)

  def LogSensorReading(self, sensor_name, temperature, when):
    sensor = self._GetSensorFromName(sensor_name)
    res = models.Thermolog.objects.create(site=self._site, sensor=sensor,
        temp=temperature, time=when)
    res.save()
    return protolib.ToProto(res)

  def GetAuthToken(self, auth_device, token_value):
    try:
      return protolib.ToProto(models.AuthenticationToken.objects.get(
          site=self._site, auth_device=auth_device, token_value=token_value))
    except models.AuthenticationToken.DoesNotExist:
      return None
