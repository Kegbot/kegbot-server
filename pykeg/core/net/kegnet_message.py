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

  def ParseValue(self, value):
    self._Validate(value)
    return value

class StringField(Field):
  def ParseValue(self, val):
    val = self._FlattenListValue(val)
    return str(val)

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
    def getter(self, name=name):
      return self._values[name]
    def setter(self, value, name=name):
      parser = self._fields[name]
      self._values[name] = parser.ParseValue(value)
    setattr(cls, name, property(getter, setter))


class Message(BaseMessage):

  class ValidationError(Exception):
    """Raised when message is not valid."""

  def Validate(self):
    """Raises an exception if message is not valid."""
    raise NotImplementedError

  def __init__(self, initial=None, **kwargs):
    self._fields = self.class_fields.copy()
    self._values = dict((k, None) for k in self.class_fields.keys())

    if initial is not None:
      self._UpdateFromDict(initial)
    else:
      self._UpdateFromDict(kwargs)

  def __str__(self):
    vallist = ('%s=%s' % (k, v) for k, v in self._values.iteritems())
    return '<%s>' % (', '.join(vallist))

  def __iter__(self):
    for name, field in self._GetFields().items():
      yield field

  def _GetFields(self):
    return self._fields

  def _UpdateFromDict(self, d):
    for k, v in d.iteritems():
      setattr(self, k, v)

  @classmethod
  def FromJson(cls, json_str):
    d = simplejson.loads(json_str)
    return cls(initial=d)

  def AsDict(self):
    ret = {}
    for k, v in self._fields.iteritems():
      ret[k] = self._values.get(k)
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

m = ThermoUpdateMessage()
m.sensor_name = 'foo'
print m
print m.sensor_name
