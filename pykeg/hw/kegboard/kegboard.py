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
from pykeg.hw.kegboard import crc16

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


### Fields

class Field(util.BaseField):
  def __init__(self, tagnum):
    self.tagnum = tagnum

  def ToBytes(self, value):
    raise NotImplementedError

  def ToString(self, value):
    return str(value)


class StructField(Field):
  _STRUCT_FORMAT = '<'
  def __init__(self, tagnum):
    Field.__init__(self, tagnum)
    self._packed_size = struct.calcsize(self._STRUCT_FORMAT)

  def ParseValue(self, value):
    if len(value) != self._packed_size:
      raise ValueError, "Bad length, must be exactly %i bytes" % (self._packed_size,)
    return struct.unpack(self._STRUCT_FORMAT, value)[0]

  def ToBytes(self, value):
    return struct.pack(self._STRUCT_FORMAT, value)


class Uint16Field(StructField):
  _STRUCT_FORMAT = '<H'


class Uint32Field(StructField):
  _STRUCT_FORMAT = '<I'


class Uint64Field(StructField):
  _STRUCT_FORMAT = '<Q'


class OnewireIdField(Uint64Field):
  def ToString(self, value):
    return "0x%x" % (value,)


class StringField(Field):
  def ParseValue(self, bytes):
    return bytes.strip('\x00')

  def ToBytes(self, value):
    return str(value) + '\x00'


class OutputField(Uint16Field):
  def ParseValue(self, bytes):
    if bytes.strip('\x00'):
      return 1
    else:
      return 0

  def ToString(self, value):
    if value:
      return 'on'
    else:
      return 'off'


class TempField(Uint32Field):
  def ParseValue(self, value):
    value = Uint32Field.ParseValue(self, value)
    value /= 1000000.0
    return value


### Message types

class Message(util.BaseMessage):
  def __init__(self, initial=None, bytes=None, **kwargs):
    util.BaseMessage.__init__(self, initial, **kwargs)
    self._tag_to_field = {}
    for field in self._fields.itervalues():
      self._tag_to_field[field.tagnum] = field
    if bytes is not None:
      self.UnpackFromBytes(bytes)

  def UnpackFromBytes(self, bytes):
    if len(bytes) < 16:
      raise ValueError, "Not enough bytes"

    header = bytes[:12]
    payload = bytes[12:-4]
    trailer = bytes[-4:]
    crcd_bytes = bytes[:-2]

    prefix, message_id, message_len = struct.unpack('<8sHH', header)

    if len(payload) != message_len:
      raise ValueError, "Payload size does not match tag"

    checked_crc = crc16.crc16_ccitt(crcd_bytes)
    # TODO(mikey): assert checked_crc == 0

    pos = 0
    while pos+2 <= len(payload):
      tag, vallen  = struct.unpack('<BB', payload[pos:pos+2])
      pos += 2
      valbytes = payload[pos:pos+vallen]
      pos += vallen
      field = self._tag_to_field.get(tag)
      if field:
        setattr(self, field.name, valbytes)
      else:
        # unknown tag
        pass

  def ToBytes(self):
    payload = ''
    for field_name, field in self._fields.iteritems():
      field_bytes = field.ToBytes(self._values[field_name])
      payload += struct.pack('<BB', field.tagnum, len(field_bytes))
      payload += field_bytes

    out = 'KBSP v1:'
    out += struct.pack('<HH', self.MESSAGE_ID, len(payload))
    out += payload
    crc = crc16.crc16_ccitt(out)
    out += struct.pack('<H', crc)
    out += '\r\n'
    return out

class HelloMessage(Message):
  MESSAGE_ID = 0x01
  protocol_version = Uint16Field(0x01)


class ConfigurationMessage(Message):
  MESSAGE_ID = 0x02
  board_name = StringField(0x01)
  baud_rate = Uint16Field(0x02)
  update_interval = Uint16Field(0x03)


class MeterStatusMessage(Message):
  MESSAGE_ID = 0x10
  meter_name = StringField(0x01)
  meter_reading = Uint32Field(0x02)


class TemperatureReadingMessage(Message):
  MESSAGE_ID = 0x11
  sensor_name = StringField(0x01)
  sensor_reading = TempField(0x02)


class OutputStatusMessage(Message):
  MESSAGE_ID = 0x12
  output_name = StringField(0x01)
  output_reading = OutputField(0x02)


class OnewirePresenceMessage(Message):
  MESSAGE_ID = 0x13
  device_id = OnewireIdField(0x01)


MESSAGE_ID_TO_CLASS = {}
for cls in Message.__subclasses__():
  idnum = cls.MESSAGE_ID
  if idnum in MESSAGE_ID_TO_CLASS:
    raise RuntimeError, "More than one message for id: %i" % (idnum,)
  MESSAGE_ID_TO_CLASS[idnum] = cls


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
