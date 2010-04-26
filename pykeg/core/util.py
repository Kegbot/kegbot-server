# Copyright 2008 Mike Wakerly <opensource@hoho.com>
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

"""General purpose utilities, bits, and bobs"""

import asyncore
import errno
import os
import sys
import types
import threading
import traceback
import logging

### Misc classes
def Enum(*defs):
  """http://code.activestate.com/recipes/413486/"""
  assert defs, "Empty enums are not supported"

  names = []
  namedict = {}
  idx = 0
  for item in defs:
    if type(item) == types.TupleType:
      name, idx = item
    else:
      name = item
    namedict[idx] = name
    names.append(name)
    idx += 1

  class EnumClass(object):
    __slots__ = names
    def __iter__(self):        return iter(constants)
    def __len__(self):         return len(constants)
    def __getitem__(self, i):  return constants[i]
    def __repr__(self):        return 'Enum' + str(names)
    def __str__(self):         return 'enum ' + str(constants)

  class EnumValue(object):
    __slots__ = ('__value')
    def __init__(self, value): self.__value = value
    Value = property(lambda self: self.__value)
    EnumType = property(lambda self: EnumType)
    def __hash__(self):        return hash(self.__value)
    def __cmp__(self, other):
      # C fans might want to remove the following assertion
      # to make all enums comparable by ordinal value {;))
      assert self.EnumType is other.EnumType, "Only values from the same enum are comparable"
      return cmp(self.__value, other.__value)
    def __invert__(self):      return constants[maximum - self.__value]
    def __nonzero__(self):     return bool(self.__value)
    def __repr__(self):        return str(namedict[self.__value])

  maximum = len(names) - 1
  constants = {}
  i = 0
  for item in defs:
    if type(item) == types.TupleType:
      name, idx = item
    else:
      name, idx = item, i
    assert idx not in constants
    i = idx + 1
    val = EnumValue(idx)
    setattr(EnumClass, name, val)
    constants[idx] = val
  EnumType = EnumClass()
  return EnumType


class KegbotThread(threading.Thread):
  """ Convenience wrapper around a threading.Thread """
  def __init__(self, name):
    threading.Thread.__init__(self)
    self.setName(name)
    self.setDaemon(True)
    self._quit = False
    self._logger = logging.getLogger(self.getName())
    self._started = False

  def hasStarted(self):
    return self._started

  def Quit(self):
    self._quit = True

  def GetStatus(self):
    return []

  def start(self):
    self._started = True
    threading.Thread.start(self)

  def run(self):
    try:
      self.ThreadMain()
    except:
      self._logger.error('Uncaught exception in thread %s. Stack trace:' %
          self.getName())
      LogTraceback(self._logger.error)
      self._logger.error('Exiting thread.')
      return

  def ThreadMain(self):
    pass


class AsyncoreThread(KegbotThread):
  def ThreadMain(self):
    self._logger.info('Starting up')
    while not self._quit:
      asyncore.loop(timeout=0.5, count=1)
    self._logger.info('Quitting')


class SimpleGraph:
  """Inspired by http://www.python.org/doc/essays/graphs.html"""
  def __init__(self, vertices):
    """Build up a graph with unidirectional vertices"""
    self._graph = {}
    for a, b in vertices:
      if a in self._graph:
        self._graph[a].add(b)
      else:
        self._graph[a] = set((b,))

  def ShortestPath(self, start, end, path=[]):
    path = path + [start]
    if start == end:
      return path
    if start not in self._graph:
      return None
    shortest = None
    for node in self._graph[start]:
      if node in path:
        continue
      newpath = self.ShortestPath(node, end, path)
      if newpath:
        if not shortest or len(newpath) < len(shortest):
          shortest = newpath
    return shortest


# These metaclasses are modeled after Ian Bicking's examples:
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


class BaseField(object):
  def _Validate(self, value):
    pass

  def ParseValue(self, value):
    self._Validate(value)
    return value

  def ToString(self, value):
    return str(value)


class BaseMessage(Declarative):
  class_fields = {}

  def __classinit__(cls, new_attrs):
    cls.class_fields = cls.class_fields.copy()
    for name, value in new_attrs.items():
      if isinstance(value, BaseField):
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

  def __init__(self, initial=None, **kwargs):
    self._fields = self.class_fields.copy()
    self._values = dict((k, None) for k in self.class_fields.keys())

    if initial is not None:
      self._UpdateFromDict(initial)
    else:
      self._UpdateFromDict(kwargs)

  def __str__(self):
    clsname = self.__class__.__name__
    vallist = []
    for fieldname, fieldvalue in self._values.iteritems():
      field = self._fields[fieldname]
      vallist.append('%s=%s' % (fieldname, field.ToString(fieldvalue)))
    valstr = (' '.join(vallist))
    return '<%s: %s>' % (clsname, valstr)

  def __iter__(self):
    for name, field in self._GetFields().items():
      yield field

  def __cmp__(self, other):
    if not other or type(other) != type(self):
      return -1
    return cmp(self._values, other._values)

  def _GetFields(self):
    return self._fields

  def _UpdateFromDict(self, d):
    for k, v in d.iteritems():
      setattr(self, k, v)

  def AsDict(self):
    ret = {}
    for k, v in self._fields.iteritems():
      ret[k] = self._values.get(k)
    return ret

  def SetValue(self, fieldname, value):
    if fieldname not in self._values:
      raise KeyError
    self._values[fieldname] = value


### Misc functions

def daemonize():
  # Fork once
  if os.fork() != 0:
    os._exit(0)
  os.setsid()  # Create new session
  # Fork twice
  if os.fork() != 0:
    os._exit(0)
  #os.chdir("/")
  os.umask(0)

  os.close(sys.__stdin__.fileno())
  os.close(sys.__stdout__.fileno())
  os.close(sys.__stderr__.fileno())

  os.open('/dev/null', os.O_RDONLY)
  os.open('/dev/null', os.O_RDWR)
  os.open('/dev/null', os.O_RDWR)

def instantBAC(gender, weight, alcpct, ounces):
  if alcpct <= 0:
    return 0.0

  # calculate weight in metric KGs
  if weight <= 0:
    return 0.0

  kg_weight = weight/2.2046

  # gender based water-weight
  if gender == 'male':
    waterp = 0.58
  else:
    waterp = 0.49

  # find total body water (in milliliters)
  bodywater = kg_weight * waterp * 1000.0

  # weight in grams of 1 oz alcohol
  alcweight = 29.57*0.79;

  # rate of alcohol per subject's total body water
  alc_per_body_ml = alcweight/bodywater

  # find alcohol concentration in blood (80.6% water)
  alc_per_blood_ml = alc_per_body_ml * 0.806

  # switch to "grams percent"
  grams_pct = alc_per_blood_ml * 100.0

  # determine how much we've really consumed
  alc_consumed = ounces * (alcpct/100.0)
  instant_bac = alc_consumed * grams_pct

  return instant_bac

def decomposeBAC(bac,seconds_ago,rate=0.02):
  return max(0.0,bac - (rate * (seconds_ago/3600.0)))

def str_to_addr(strdata, default_host='127.0.0.1', default_port=0):
  """Extract a tuple of (hostname, port) from a string.

  The string is specified as <hostname>:<port>. If only one value is given, it
  is treated as the <port> and the default ip will be used.
  """

  ip = default_host
  port = default_port

  if strdata is not None:
    parts = strdata.split(':')
    if len(parts) == 2:
      ip, port = parts[0], int(parts[1])
    elif len(parts) == 1:
      port = int(parts[0])

  return ip, port

def synchronized(f):
  """Decorator that synchronizes a class method with self._lock"""
  def new_f(self, *args, **kwargs):
    self._lock.acquire()
    try:
      return f(self, *args, **kwargs)
    finally:
      self._lock.release()
  return new_f

def CtoF(t):
  return ((9.0/5.0)*t) + 32

def PidIsAlive(pid):
  try:
    os.kill(pid, 0)
  except OSError, e:
    if e.errno == errno.ESRCH:
      return False
  return True

def LogTraceback(log_method, tb_tuple=None):
  if tb_tuple is None:
    tb_tuple = sys.exc_info()

  tb_type, tb_value, tb_obj = tb_tuple

  if tb_obj is None:
    log_method('No exception')
    return
  stack = traceback.extract_tb(tb_obj)
  for frame in traceback.format_list(stack):
    for line in frame.split('\n'):
      log_method('    ' + line.strip())
  log_method('Error was: %s: %s' % (tb_type, tb_value))
