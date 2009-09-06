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

"""Python interfaces to a Kegboard device."""

import logging
import struct
import string

from pykeg.core import util
from pykeg.external.gflags import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_string('kegboard_device', '/dev/ttyUSB0',
    'An explicit device file (eg /dev/ttyUSB0) on which to listen for kegboard '
    'packets.')

gflags.DEFINE_integer('kegboard_speed', 115200,
    'Baud rate of device at --kegboard_device')

KBSP_PREFIX = "KBSP v1:"


class KegboardError(Exception):
  """Generic error with Kegboard"""

class MessageError(KegboardError):
  """Generic error in Message class"""

class UnknownMessageError(MessageError):
  """Message id is not known"""

class FramingError(KegboardError):
  """Problem synchronizing with serial stream"""

### helpers

def str_to_bytes(bytes):
  return ''.join('\\x%02x' % ord(x) for x in bytes)

def str_to_printable(bytes):
  printable = lambda x: ('.', x)[x in string.letters or x in string.digits]
  return ''.join('%s  ' % printable(x) for x in bytes)


### Fields

class Field(object):
  def __init__(self, bytes=None, value=None):
    if bytes is not None and value is not None:
      raise ValueError, "Must specify only one of: bytes, value"

    self._value = None

    if bytes is not None:
      self.SetBytes(bytes)
    if value is not None:
      self.SetValue(value)

  def SetBytes(self, bytes):
    raise NotImplementedError

  def SetValue(self, value):
    self._value = value

  def GetBytes(self):
    raise NotImplementedError

  def GetValue(self):
    return self._value


class StructField(Field):
  _STRUCT_FORMAT = '<'
  def __init__(self, bytes=None, value=None):
    Field.__init__(self, bytes, value)
    self._packed_size = struct.calcsize(self._STRUCT_FORMAT)

  def SetBytes(self, bytes):
    if len(bytes) != self._packed_size:
      raise ValueError, "Bad length, must be exactly %i bytes" % (self._packed_size,)
    self.SetValue(struct.unpack(self._STRUCT_FORMAT, bytes)[0])

  def GetBytes(self):
    return struct.pack(self._STRUCT_FORMAT, self._value)


class Uint16Field(StructField):
  _STRUCT_FORMAT = '<H'


class Uint32Field(StructField):
  _STRUCT_FORMAT = '<I'


class StringField(Field):
  def SetBytes(self, bytes):
    self.SetValue(bytes.strip('\x00'))

  def GetBytes(self):
    return self._value + '\x00'


class OutputField(Uint16Field):
  def SetBytes(self, bytes):
    if bytes.strip('\x00'):
      self.SetValue(1)
    else:
      self.SetValue(0)


class TempField(Uint32Field):
  pass


### Message types

MESSAGE_ID = util.Enum(*(
  ('HELLO', 0x01),
  ('CONFIGURATION', 0x02),
  ('METER_STATUS', 0x10),
  ('TEMPERATURE_READING', 0x11),
  ('OUTPUT_STATUS', 0x12),
))


class Message(object):
  def __init__(self, bytes=None):
    self._map_tag_to_field = {}
    self._map_name_to_tag = {}
    slots = ['_map_tag_to_field', '_map_name_to_tag']
    for tag, name, fieldtype in self._FIELDS:
      var = fieldtype()
      self._map_tag_to_field[tag] = var
      self._map_name_to_tag[name] = tag
      setattr(self, name, var)
      slots.append(name)
    self.__slots__ = slots
    if bytes is not None:
      self.UnpackFromBytes(bytes)

  def __str__(self):
    vallist = []
    for k in self._map_name_to_tag.keys():
      vallist.append((k, getattr(self, k).GetValue()))
    valstr = ' '.join(('%s=%s' % x for x in vallist))
    return '<%s %s>' % (self._TYPE, valstr)

  def UnpackFromBytes(self, bytes):
    if len(bytes) < 14:
      raise ValueError, "Not enough bytes"

    header = bytes[:12]
    bytes = bytes[12:]

    prefix, message_id, message_len = struct.unpack('<8sHH', header)

    payload = bytes[:message_len]
    bytes = bytes[message_len:]

    crc = bytes[:2]
    bytes = bytes[2:]

    trailer = bytes

    if len(payload) != message_len:
      raise ValueError, "Payload size does not match tag"
    if len(crc) != 2:
      raise ValueError, "Trailer section size incorrect (%s)" % len(crc)

    pos = 0
    while pos+2 <= len(payload):
      tag, vallen  = struct.unpack('<BB', payload[pos:pos+2])
      pos += 2
      valbytes = payload[pos:pos+vallen]
      pos += vallen
      field = self._map_tag_to_field.get(tag)
      if field:
        field.SetBytes(valbytes)


  def GetBytes(self):
    payload = ''
    for tag, name, fieldtype in self._FIELDS:
      bytes = getattr(self, name).GetBytes()
      payload += struct.pack('<CC', tag, len(bytes))
      payload += bytes
    return res


class HelloMessage(Message):
  _TYPE = MESSAGE_ID.HELLO
  _FIELDS = (
    (0x01, 'protocol_version', Uint16Field),
  )


class ConfigurationMessage(Message):
  _TYPE = MESSAGE_ID.CONFIGURATION
  _FIELDS = (
    (0x01, 'board_name', StringField),
    (0x02, 'baud_rate', Uint16Field),
    (0x03, 'update_interval', Uint16Field),
  )


class MeterStatusMessage(Message):
  _TYPE = MESSAGE_ID.METER_STATUS
  _FIELDS = (
    (0x01, 'meter_name', StringField),
    (0x02, 'meter_reading', Uint32Field),
  )

class TemperatureReadingMessage(Message):
  _TYPE = MESSAGE_ID.TEMPERATURE_READING
  _FIELDS = (
      (0x01, 'sensor_name', StringField),
      (0x02, 'sensor_reading', TempField),
  )


class OutputStatusMessage(Message):
  _TYPE = MESSAGE_ID.OUTPUT_STATUS
  _FIELDS = (
    (0x01, 'output_name', StringField),
    (0x02, 'output_reading', OutputField),
  )


MESSAGE_ID_TO_CLASS = {}
for cls in Message.__subclasses__():
  MESSAGE_ID_TO_CLASS[cls._TYPE.Value] = cls


def GetHeaderFromBytes(bytes):
  if len(bytes) < 12:
    raise ValueError, "Not enough bytes to get header"
  prefix, message_id, message_len = struct.unpack('<8sHH', bytes[:12])
  return prefix, message_id, message_len

def GetMessageForBytes(bytes):
  if len(bytes) < 6:
    raise ValueError, "Not enough bytes"
  prefix, message_id = struct.unpack('<8sH', bytes[:10])
  cls = MESSAGE_ID_TO_CLASS.get(message_id)
  if not cls:
    raise UnknownMessageError
  return cls(bytes=bytes)


class KegboardReader(object):
  def __init__(self, fd):
    self._logger = logging.getLogger('kegboard-reader')
    self._fd = fd
    self._framing_lost_count = 0

  def FixFraming(self):
    """Read the stream until a packet prefix is discovered."""
    self._logger.info('Framing broken, fixing')
    bytes_read = 0
    found_prefix = ""
    while True:
      b = self._fd.read(1)
      bytes_read += 1
      found_prefix += b
      if found_prefix.endswith(KBSP_PREFIX):
        self._logger.info('Found start of frame, framing fixed.')
        break
      if bytes_read > 2048:
        self._logger.error('Could not fix framing.')
        raise FramingError, "Could not fix framing after 2048 bytes"
    self._framing_lost_count += 1

  def GetNextMessage(self):
    prefix = self._fd.read(8)
    if prefix != KBSP_PREFIX:
      self.FixFraming()
    header = KBSP_PREFIX + self._fd.read(4)
    prefix, message_id, message_len = GetHeaderFromBytes(header)
    payload = self._fd.read(message_len)
    trailer = self._fd.read(4)
    return GetMessageForBytes(header + payload + trailer)

