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

### Field classes
class Field(object):
  def __init__(self, value=None):
    self._value = value

  def _Validate(self, value):
    pass

  def _FlattenListValue(self, value):
    if isinstance(value, basestring):
      return value
    elif getattr(value, '__iter__', False):
      if len(value) != 1:
        raise ValueError, 'Must give exactly one item'
      return value[0]
    return value

  def SetValue(self, value):
    self._Validate(value)
    self._value = value

  def GetValue(self):
    return self._value

class StringField(Field):
  def SetValue(self, val):
    val = self._FlattenListValue(val)
    self._value = str(val)

class PositiveIntegerField(Field):
  def SetValue(self, val):
    val = self._FlattenListValue(val)
    intval = int(val)
    if intval < 0:
      raise ValueError, 'A positive integer is required'
    self._value = intval

class FloatField(Field):
  def SetValue(self, val):
    val = self._FlattenListValue(val)
    self._value = float(val)

### Message classes
# These metaclasses are modeled after Ian Bicking's example:
# http://blog.ianbicking.org/a-conservative-metaclass.html

class DeclarativeMeta(type):
  def __new__(meta, class_name, bases, new_attrs):
    cls = type.__new__(meta, class_name, bases, new_attrs)
    cls.__classinit__.im_func(cls, new_attrs)
    return cls

class Declarative(object):
  __metaclass__ = DeclarativeMeta
  def __classinit__(cls, new_attrs):
    pass

class BaseMessage(Declarative):
  class_fields = {}

  def __classinit__(cls, new_attrs):
    cls.class_fields = cls.class_fields.copy()
    for name, value in new_attrs.items():
      if isinstance(value, Field):
        cls.add_field(name, value)

  @classmethod
  def add_field(cls, name, field):
    cls.class_fields[name] = field
    field.name = name


class Message(BaseMessage):

  class ValidationError(Exception):
    """Raised when message is not valid."""

  def Validate(self):
    """Raises an exception if message is not valid."""
    raise NotImplementedError

  def __init__(self, initial=None, **kwargs):
    self._fields = self.class_fields.copy()
    #for name, field in self._fields.iteritems():
    #  prop = property(field.GetValue, field.SetValue)
    #  setattr(self, name, prop)

    if initial is not None:
      self._UpdateFromDict(initial)
    else:
      self._UpdateFromDict(kwargs)

  def __str__(self):
    vallist = ('%s=%s' % (k, v.GetValue()) for k, v in self._fields.iteritems())
    return '<%s>' % (', '.join(vallist))

  def __iter__(self):
    for name, field in self._fields.items():
      yield field

  def __getitem__(self, name):
    return self._fields[name]

  def _UpdateFromDict(self, d):
    for k, v in d.iteritems():
      if k not in self._fields:
        raise ValueError, 'Unknown key: %s' % k
      self._fields[k].SetValue(v)

  @classmethod
  def FromJson(cls, json_str):
    d = simplejson.loads(json_str)
    return cls(initial=d)

  def AsDict(self):
    ret = {}
    for k, v in self._fields.iteritems():
      ret[k] = v.GetValue()
    return ret

  def AsJson(self):
    return simplejson.dumps(self.AsDict())


class FlowUpdateMessage(Message):
  tap_name = StringField()
  meter_reading = PositiveIntegerField()


class FlowStartMessage(Message):
  tap_name = StringField()


class FlowStopMessage(Message):
  tap_name = StringField()


class ThermoUpdateMessage(Message):
  sensor_name = StringField()
  sensor_value = FloatField()

