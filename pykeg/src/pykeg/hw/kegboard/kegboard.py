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

import cStringIO
import errno
import glob
import logging
import struct
import string

import gflags

from pykeg.core import util
from pykeg.hw.kegboard import crc16

_DEVICES = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/cu.usbserial*')
if _DEVICES:
  _DEFAULT_PORT = _DEVICES[0]
else:
  _DEFAULT_PORT = '/dev/ttyUSB0'

FLAGS = gflags.FLAGS

gflags.DEFINE_string('kegboard_device', _DEFAULT_PORT,
    'An explicit device file (eg /dev/ttyUSB0) on which to listen for kegboard '
    'packets.')

gflags.DEFINE_integer('kegboard_speed', 115200,
    'Baud rate of device at --kegboard_device')

KBSP_PREFIX = "KBSP v1:"
KBSP_PAYLOAD_MAXLEN = 112
KBSP_TRAILER = "\r\n"

class KegboardError(Exception):
  """Generic error with Kegboard"""

class MessageError(KegboardError):
  """Generic error in Message class"""

class UnknownMessageError(MessageError):
  """Message id is not known"""

class FramingError(KegboardError):
  """Problem synchronizing with serial stream"""

### Helpers

def bytes_to_hexstr(bytestr):
  """Like repr(s), but pritns all characters as hex."""
  return ''.join('\\x%02x' % ord(c) for c in bytestr)

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


class Uint8Field(StructField):
  _STRUCT_FORMAT = 'B'


class Uint16Field(StructField):
  _STRUCT_FORMAT = '<H'


class Int32Field(StructField):
  _STRUCT_FORMAT = '<i'


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


class BytesField(Field):
  def ToString(self, value):
    return '0x%s' % ''.join('%02x' % ord(c) for c in value)

  def ParseValue(self, bytes):
    return bytes

  def ToBytes(self, value):
    return value


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


class TempField(Int32Field):
  def ParseValue(self, value):
    value = Int32Field.ParseValue(self, value)
    value /= 1000000.0
    return value


### Message types

class Message(util.BaseMessage):
  def __init__(self, initial=None, bytes=None, payload_bytes=None, **kwargs):
    util.BaseMessage.__init__(self, initial, **kwargs)
    self._tag_to_field = {}
    for field in self._fields.itervalues():
      self._tag_to_field[field.tagnum] = field
    if bytes is not None:
      self.UnpackFromBytes(bytes)
    if payload_bytes is not None:
      self.UnpackFromPayload(payload_bytes)

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

    # TODO(mikey): assert checked_crc == 0
    checked_crc = crc16.crc16_ccitt(crcd_bytes)
    self.UnpackFromPayload(payload)

  def UnpackFromPayload(self, payload):
    pos = 0
    payload_len = len(payload)
    while (pos + 2) <= payload_len:
      fieldlen = self._ParseField(payload[pos:])
      pos += 2 + fieldlen

  def _ParseField(self, field_bytes):
    tag, length = struct.unpack('<BB', field_bytes[:2])
    data = field_bytes[2:2+length]
    # If field number is known, set its value. (Ignore it otherwise.)
    field = self._tag_to_field.get(tag)
    if field:
      setattr(self, field.name, data)
    return length

  def ToBytes(self):
    payload = cStringIO.StringIO()
    for field_name, field in self._fields.iteritems():
      field_bytes = field.ToBytes(self._values[field_name])
      payload.write(struct.pack('<BB', field.tagnum, len(field_bytes)))
      payload.write(field_bytes)

    payload_str = payload.getvalue()
    payload.close()

    out = cStringIO.StringIO()
    out.write(KBSP_PREFIX)
    out.write(struct.pack('<HH', self.MESSAGE_ID, len(payload_str)))
    out.write(payload_str)
    crc = crc16.crc16_ccitt(out.getvalue())
    out.write(struct.pack('<H', crc))
    out.write('\r\n')
    return out.getvalue()

class HelloMessage(Message):
  MESSAGE_ID = 0x01
  firmware_version = Uint16Field(0x01)


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
  """Deprecated."""
  MESSAGE_ID = 0x13
  device_id = OnewireIdField(0x01)
  status = Uint8Field(0x02)


class AuthTokenMessage(Message):
  MESSAGE_ID = 0x14
  device = StringField(0x01)
  token = BytesField(0x02)
  status = Uint8Field(0x03)


class PingCommand(Message):
  MESSAGE_ID = 0x81


class SetOutputCommand(Message):
  MESSAGE_ID = 0x84
  output_id = Uint8Field(0x01)
  output_mode = OutputField(0x02)


MESSAGE_ID_TO_CLASS = {}
for cls in Message.__subclasses__():
  idnum = cls.MESSAGE_ID
  if idnum in MESSAGE_ID_TO_CLASS:
    raise RuntimeError, "More than one message for id: %i" % (idnum,)
  MESSAGE_ID_TO_CLASS[idnum] = cls


def GetMessageForBytes(bytes):
  if len(bytes) < 6:
    raise ValueError, "Not enough bytes"
  prefix, message_id = struct.unpack('<8sH', bytes[:10])
  cls = MESSAGE_ID_TO_CLASS.get(message_id)
  if not cls:
    raise UnknownMessageError
  return cls(bytes=bytes)


def GetMessageById(message_id, payload_bytes=None):
  cls = MESSAGE_ID_TO_CLASS.get(message_id)
  if not cls:
    raise UnknownMessageError
  return cls(payload_bytes=payload_bytes)


class KegboardReader(object):
  def __init__(self, fd):
    self._logger = logging.getLogger('kegboard-reader')
    self._fd = fd

  def _read(self, count):
    """Wrapper for fd read which handles EAGAIN."""
    attempts = 0
    while attempts < 100:
      try:
        return self._fd.read(count)
      except OSError, e:
        if e.errno == errno.EAGAIN:
          attempts += 1
          continue
        raise e
    raise RuntimeError('Read caused EAGAIN too many times.')

  def WriteMessage(self, message):
    if not isinstance(message, Message):
      raise ValueError, "WriteMessage must be called with a Message instance"
    self._fd.write(message.ToBytes())

  def GetNextMessage(self):
    header_pos = 0
    header_len = len(KBSP_PREFIX)
    while True:
      # Find the prefix, re-aligning the messages as needed.
      logged_frame_error = False
      while header_pos < header_len:
        byte = self._read(1)
        if byte == KBSP_PREFIX[header_pos]:
          # Got the expected byte.
          header_pos += 1
          if logged_frame_error:
            self._logger.info('Packet framing fixed.')
            logged_frame_error = False
        else:
          # Wrong byte, log the error and start over.
          if not logged_frame_error:
            expected = KBSP_PREFIX[header_pos]
            self._logger.info('Packet framing broken (found %s, expected %s); '
                              'reframing.' % (repr(byte), repr(expected)))
            logged_frame_error = True
          if byte == KBSP_PREFIX[0]:
            header_pos = 1
          else:
            header_pos = 0

      # Read message type and message length.
      header_bytes = self._read(4)
      message_id, message_len = struct.unpack('<HH', header_bytes)
      if message_len > KBSP_PAYLOAD_MAXLEN:
        self._logger.warning('Bogus message length (%i), skipping message' %
                             message_len)
        header_pos = 0
        continue

      # Read payload and trailer.
      payload = self._read(message_len)
      crc = self._read(2)
      trailer = self._read(2)

      if trailer != KBSP_TRAILER:
        self._logger.warning('Bad trailer (%s), skipping message' %
                             repr(trailer))
        # Bogus trailer; start over.
        header_pos = 0
        continue

      if FLAGS.verbose:
        rawstr = ''.join((header_bytes, payload, crc, trailer))
        rawstr = bytes_to_hexstr(rawstr)
        dumpstr = 'ID=%i PAYLOAD=%s' % (message_id, bytes_to_hexstr(payload))
        self._logger.debug('RX: %s' % rawstr)
        self._logger.debug(dumpstr)

      return GetMessageById(message_id, payload)
