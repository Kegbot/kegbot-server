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

from pykeg.core import kb_common

class BackendError(Exception):
  """Base backend error exception."""

class NoTokenError(BackendError):
  """Token given is unknown."""

class Backend:
  """Abstract base Kegbot backend class.

  This class defines the interface that pykeg uses to talk to the kegbot
  backend.
  """

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

  def RecordDrink(self, tap_name, ticks, volume_ml=None, username=None,
      pour_time=None, duration=0, auth_token=None, spilled=False,
      shout=''):
    """Records a new drink with the given parameters."""
    raise NotImplementedError

  def CancelDrink(self, seqn, spilled=False):
    """Cancels the given drink.

    If `spilled` is False, the drink will be canceled as if it never occurred.
    Otherwise, the drink will be canceled, and the volume associated with it
    will be transfered to its keg's spilled total.
    """
    raise NotImplementedError

  def LogSensorReading(self, sensor_name, temperature, when=None):
    """Records a new sensor reading."""
    raise NotImplementedError

  def GetAuthToken(self, auth_device, token_value):
    """Returns an AuthenticationToken instance."""
    raise NotImplementedError

