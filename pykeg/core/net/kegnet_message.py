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

"""Messages exchanged over Kegnet api connections."""

import simplejson

from pykeg.core import util

### Field classes

# TODO(mikey): rename me to something more descriptive
class Field(util.BaseField):
  def _FlattenListValue(self, value):
    if isinstance(value, basestring):
      return value
    elif getattr(value, '__iter__', False):
      if len(value) != 1:
        raise ValueError, 'Must give exactly one item'
      return value[0]
    return value

class StringField(Field):
  def ParseValue(self, val):
    val = self._FlattenListValue(val)
    if val is not None:
      return str(val)
    else:
      return None

class PositiveIntegerField(Field):
  def ParseValue(self, val):
    val = self._FlattenListValue(val)
    intval = int(val)
    if intval < 0:
      raise ValueError, 'A positive integer is required'
    return intval

class FloatField(Field):
  def ParseValue(self, val):
    val = self._FlattenListValue(val)
    return float(val)

class DateTimeField(Field):
  def ParseValue(self, val):
    return str(val)

### Message classes

class Message(util.BaseMessage):

  class ValidationError(Exception):
    """Raised when message is not valid."""

  def Validate(self):
    """Raises an exception if message is not valid."""
    raise NotImplementedError

  @classmethod
  def FromJson(cls, json_str):
    d = simplejson.loads(json_str)
    return cls(initial=d)

  def AsJson(self):
    return simplejson.dumps(self.AsDict(), sort_keys=True, indent=4)


class PingMessage(Message):
  """No-op message."""


class MeterUpdateMessage(Message):
  """Message emitted when a meter reading changes."""
  tap_name = StringField()
  meter_reading = PositiveIntegerField()


class FlowStartRequestMessage(Message):
  """Message emitted to request force-start of a flow."""
  tap_name = StringField()


class FlowStopRequestMessage(Message):
  """Message emitted to request force-stop of a flow."""
  tap_name = StringField()


class FlowStatusRequestMessage(Message):
  """Message emitted to request force-stop of a flow."""
  tap_name = StringField()


class TapIdleMessage(Message):
  """Message emitted when a flow has become idle."""
  tap_name = StringField()


class ThermoUpdateMessage(Message):
  """Message emitted when a temperature sensor reading changes."""
  sensor_name = StringField()
  sensor_value = FloatField()


class FlowUpdateMessage(Message):
  tap_name = StringField()
  start_time = DateTimeField()
  end_time = DateTimeField()
  ticks = FloatField()
  volume_ml = FloatField()
  user = StringField()

  @classmethod
  def FromFlow(cls, flow):
    msg = cls()
    msg.tap_name = flow.GetTap().GetName()
    msg.start_time = flow.GetStartTime()
    msg.end_time = flow.GetEndTime()
    msg.ticks = flow.GetTicks()
    msg.volume_ml = flow.GetVolumeMl()
    msg.user = flow.GetUser()
    return msg

class DrinkCreatedMessage(Message):
  tap_name = StringField()
  drink_id = PositiveIntegerField()
  keg_id = PositiveIntegerField()
  start_time = DateTimeField()
  end_time = DateTimeField()
  volume = FloatField()
  user = StringField()

  @classmethod
  def FromFlowAndDrink(cls, flow, drink):
    msg = cls()
    msg.tap_name = flow.tap_name
    msg.start_time = drink.starttime
    msg.end_time = drink.endtime
    msg.volume = float(drink.Volume())
    if drink.keg:
      msg.keg_id = drink.keg.id
    else:
      msg.keg_id = 0
    msg.user = drink.user.username
    msg.drink_id = drink.id
    return msg


class AuthUserAddMessage(Message):
  tap_name = StringField()
  user_name = StringField()


class AuthUserRemoveMessage(Message):
  tap_name = StringField()
  user_name = StringField()


class AuthTokenAddMessage(Message):
  tap_name = StringField()
  auth_device_name = StringField()
  token_value = StringField()
