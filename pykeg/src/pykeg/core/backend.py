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

from pykeg.billing import models as billing_models
from pykeg.core import kb_common
from pykeg.core import config
from pykeg.core import models

class Backend:
  """Abstract base Kegbot backend class.

  This class defines the interface that pykeg uses to talk to the kegbot
  backend.
  """

  def GetDefaultUser(self):
    """Returns the User which should be used for pours with no known user."""
    raise NotImplementedError

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

  def GetKegForTap(self, tap_name):
    """Returns the currently-active keg for the given tap name, or None."""
    raise NotImplementedError

  def CreateDrink(self, ticks, volume_ml, starttime, endtime, user, keg=None,
      status='valid'):
    """Records a new drink with the given parameters."""
    raise NotImplementedError

  def GetSensorFromName(self, name):
    """Returns a sensor instance corresponding to name, or None."""
    raise NotImplementedError

  def CreateSensor(self, raw_name, nice_name):
    """Creates a new Sensor record with the raw_name and nice_name given."""
    raise NotImplementedError

  def LogSensorReading(self, sensor, temperature, when):
    """Records a new sensor reading."""
    raise NotImplementedError

  def GetAuthToken(self, auth_device, token_value):
    """Returns an AuthenticationToken instance."""
    raise NotImplementedError

  def CreateAuthToken(self, auth_device, token_value):
    """Creates a new AuthenticationToken instance."""
    raise NotImplementedError

  def GetBillAcceptors(self):
    """Returns all active BillAcceptor instances."""
    raise NotImplementedError

  def RecordBillAcceptorCredit(self, amount, acceptor, user=None):
    """Records a credit on the given acceptor for amount."""
    raise NotImplementedError


class KegbotBackend(Backend):
  """Django models backed Backend."""

  def __init__(self):
    self._logger = logging.getLogger('backend')
    self._config = config.KegbotConfig(self._GetConfigDict())

  def _GetConfigDict(self):
    ret = {}
    for row in models.Config.objects.all():
      ret[row.key] = row.value
    return ret

  def GetDefaultUser(self):
    DEFAULT_USER_LABELNAME = '__default_user__'

    label_q = models.UserLabel.objects.filter(labelname=DEFAULT_USER_LABELNAME)
    if not len(label_q):
      raise kb_common.ConfigurationError, ('Default user label "%s" not found.' % DEFAULT_USER_LABELNAME)

    user_q = label_q[0].userprofile_set.all()
    if not len(user_q):
      raise kb_common.ConfigurationError, ('No users found with label "%s"; need at least one.' % DEFAULT_USER_LABELNAME)

    default_user = user_q[0].user
    self._logger.info('Default user for unknown flows: %s' % str(default_user))
    return default_user

  def GetConfig(self):
    return self._config

  def GetUserFromUsername(self, username):
    matches = models.User.objects.filter(username=username)
    if not matches.count() == 1:
      return None
    return matches[0]

  def CreateNewUser(self, username, gender=kb_common.DEFAULT_NEW_USER_GENDER,
      weight=kb_common.DEFAULT_NEW_USER_WEIGHT):
    u = models.User(username=username)
    u.save()
    p = u.get_profile()
    p.gender = gender
    p.weight = weight
    p.save()
    return u

  def GetAllTaps(self):
    return models.KegTap.objects.all()

  def GetKegForTap(self, tap_name):
    try:
      tap = models.KegTap.objects.get(meter_name=tap_name)
      return tap.current_keg
    except models.KegTap.DoesNotExist:
      return None

  def CreateDrink(self, ticks, volume_ml, starttime, endtime, user, keg=None,
      status='valid'):
    d = models.Drink(ticks=int(ticks), volume_ml=volume_ml, starttime=starttime,
        endtime=endtime, user=user, keg=keg, status=status)
    d.save()
    return d

  def GetSensorFromName(self, name):
    try:
      return models.ThermoSensor.objects.get(raw_name=name)
    except models.ThermoSensor.DoesNotExist:
      return None

  def CreateSensor(self, raw_name, nice_name):
    return models.ThermoSensor.objects.create(raw_name=raw_name,
        nice_name=nice_name)

  def LogSensorReading(self, sensor, temperature, when):
    return models.Thermolog.objects.create(sensor=sensor, temp=temperature,
        time=when)

  def GetAuthToken(self, auth_device, token_value):
    try:
      return models.AuthenticationToken.objects.get(auth_device=auth_device,
        token_value=token_value)
    except models.AuthenticationToken.DoesNotExist:
      return None

  def CreateAuthToken(self, auth_device, token_value):
    return models.AuthenticationToken.objects.create(auth_device=auth_device,
        token_value=token_value)

  def GetBillAcceptors(self):
    return billing_models.BillAcceptor.objects.all()

  def RecordBillAcceptorCredit(self, amount, acceptor, user=None):
    return billing_models.Credit.objects.create(amount=amount,
        acceptor=acceptor, user=user)

