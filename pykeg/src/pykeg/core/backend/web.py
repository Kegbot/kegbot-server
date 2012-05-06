# Copyright 2012 Mike Wakerly <opensource@hoho.com>
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

"""Kegbot API implementation of Backend."""

import logging
import socket

from . import backend

from pykeg.core import kb_common
from pykeg.web.api import krest

class WebBackend(backend.Backend):
  def __init__(self, api_url=None, api_key=None):
    self._logger = logging.getLogger('api-backend')
    self._client = krest.KrestClient(api_url=api_url, api_key=api_key)

  def CreateNewUser(self, username, gender=kb_common.DEFAULT_NEW_USER_GENDER,
      weight=kb_common.DEFAULT_NEW_USER_WEIGHT):
    raise NotImplementedError

  def CreateAuthToken(self, auth_device, token_value, username=None):
    raise NotImplementedError

  def GetAllTaps(self):
    ts = self._client.TapStatus()
    return [d.tap for d in self._client.TapStatus().taps]

  def RecordDrink(self, tap_name, ticks, volume_ml=None, username=None,
      pour_time=None, duration=0, auth_token=None, spilled=False, shout=''):
    return self._client.RecordDrink(tap_name=tap_name, ticks=ticks,
        volume_ml=volume_ml, username=username, pour_time=pour_time,
        duration=duration, auth_token=auth_token, spilled=spilled,
        shout=shout)

  def CancelDrink(self, seqn, spilled=False):
    return self._client.CancelDrink(seqn, spilled)

  def LogSensorReading(self, sensor_name, temperature, when=None):
    # If the temperature is out of bounds, reject it.
    min_val = kb_common.THERMO_SENSOR_RANGE[0]
    max_val = kb_common.THERMO_SENSOR_RANGE[1]
    if temperature < min_val or temperature > max_val:
      raise ValueError, 'Temperature out of bounds'

    try:
      return self._client.LogSensorReading(sensor_name, temperature, when)
    except krest.NotFoundError:
      self._logger.warning('No sensor on backend named "%s"' % (sensor_name,))
      return None
    except krest.ServerError:
      self._logger.warning('Server error recording temperature; dropping reading.')
      return None
    except socket.error:
      self._logger.warning('Socket error recording temperature; dropping reading.')
      return None

  def GetAuthToken(self, auth_device, token_value):
    try:
      return self._client.GetToken(auth_device, token_value)
    except krest.NotFoundError:
      raise backend.NoTokenError
    except socket.error:
      self._logger.warning('Socket error fetching token; ignoring.')
      raise backend.NoTokenError
