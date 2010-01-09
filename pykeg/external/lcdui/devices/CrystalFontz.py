"""Device definitions and driver for CrystalFontz displays."""

import logging
import Queue
import select
import string
import struct
import time

from lcdui.core import crc16
from lcdui.core import cstruct
from lcdui.devices import Generic


class CrystalFontzException(Exception):
  """Generic top-level exception."""

FRAME_TYPE_HOST_COMMAND = 0x00
FRAME_TYPE_DEVICE_RESPONSE = 0x01
FRAME_TYPE_DEVICE_REPORT = 0x02
FRAME_TYPE_DEVICE_ERROR = 0x03

### Packet definitions

class CFA635Packet:
  def __init__(self, **kwargs):
    self._payload = cstruct.cStruct(fields=self.FORMAT)
    self._frame_type = FRAME_TYPE_HOST_COMMAND
    for key, val in kwargs.iteritems():
      setattr(self._payload, key, val)

  def UnpackPayload(self, payload_bytes):
    self._payload = cstruct.cstruct(fields=self.FORMAT)
    self._payload.unpack(payload_bytes)

  def Pack(self):
    command_header = self._frame_type << 6 | (self.TYPE & 0x3f)
    payload_bytes = self._payload.pack()
    payload_len = len(payload_bytes)

    bytes = struct.pack('BB', command_header, payload_len)
    bytes += payload_bytes

    crc = self.CRCMake(bytes)

    return bytes + struct.pack('H', crc)

  def CRCMake(self, data, seed = 0x0FFFF):
    return (~crc16.crc16(data, seed)) & 0x0ffff


class KeyActivityPacket(CFA635Packet):
  TYPE = 0
  FORMAT = (
    ('B', 'act_type'),
  )
  _KEY_EVENTS = {
      1: ('up','press'),
      2: ('down','press'),
      3: ('left','press'),
      4: ('right', 'press'),
      5: ('enter', 'press'),
      6: ('exit', 'press'),
      7: ('up','release'),
      8: ('down','release'),
      9: ('left','release'),
      10: ('right', 'release'),
      11: ('enter', 'release'),
      12: ('exit', 'release'),
  }
  UNKNOWN_EVENT = ('unknown', 'unknown')

  def Activity(self, var=None):
    if not var:
      var = self.act_type
    return self._KEY_EVENTS.get(var, self.UNKNOWN_EVENT)


class GetFirmwareInfo(CFA635Packet):
  TYPE = 1
  FORMAT = (
    ('s', 'data'),
  )


class WriteUserData(CFA635Packet):
  TYPE = 2
  FORMAT = (
    ('s', 'data', ' '*16),
  )


class ReadUserData(CFA635Packet):
  TYPE = 3
  FORMAT = (
    ('s', 'data'),
  )


class StoreBootState(CFA635Packet):
  TYPE = 4
  FORMAT = ( )


class RebootDevice(CFA635Packet):
  TYPE = 5
  FORMAT = (
    ('B', 8),
    ('B', 18),
    ('B', 99),
 )


class ClearScreenPacket(CFA635Packet):
  TYPE = 6
  FORMAT = ( )


# cmd 7 deprecated
# cmd 8 deprecated

class SetCharacter(CFA635Packet):
  TYPE = 9
  FORMAT = (
    ('B', 'index'),
    ('s', 'chardata'),
  )


class ReadMemory(CFA635Packet):
  TYPE = 10
  FORMAT = (
    ('B', 'address'),
  )


class SetCursorPosPacket(CFA635Packet):
  TYPE = 11
  FORMAT = (
    ('B', 'col'),
    ('B', 'row'),
  )


class SetCursorStylePacket(CFA635Packet):
  TYPE = 12
  FORMAT = (
    ('B', 'style'),
  )


class SetContrastPacket(CFA635Packet):
  TYPE = 13
  FORMAT = (
    ('B', 'amount'),
  )


class SetBacklightPacket(CFA635Packet):
  TYPE = 14
  FORMAT = (
    ('B', 'amount'),
  )


# cmd 15 deprecated
# cmd 16 fan reporting
# cmd 17 set fan power
# cmd 18 read dow device info
# cmd 19 setup temperature recording
# cmd 20 arbitrary dow transaction
# cmd 21 deprecated

class SendHDCommandPacket(CFA635Packet):
  TYPE = 22
  FORMAT = (
    ('B', 'location'),
    ('B', 'data'),
  )


class ConfigKeypadPacket(CFA635Packet):
  TYPE = 23
  FORMAT = (
    ('B', 'pressmask'),
    ('B', 'releasemask'),
  )


class ReadKeypadPacket(CFA635Packet):
  TYPE = 24
  FORMAT = (  ) #XXX todo request/reply differences


# cmd 25 set fan power fail state
# cmd 26 set fan tach glitch delay
# cmd 27 query fan power and fail-safe mask
# cmd 28 set atx power switch function
# cmd 29 enable/disable/reset watchdog

class ReadReportingPacket(CFA635Packet):
  TYPE = 30
  FORMAT = (  ) # XXX TODO


class WriteDataPacket(CFA635Packet):
  TYPE = 31
  FORMAT = (
    ('B', 'col'),
    ('B', 'row'),
    ('s', 'data'),
  )


# cmd 32 reserved

class SetBaudRatePacket(CFA635Packet):
  TYPE = 33
  FORMAT = (
    ('B', 'rate'),
  )


class ConfigGPIOPacket(CFA635Packet):
  TYPE = 34
  FORMAT = (
    ('B', 'index'),
    ('B', 'state'),
    ('B', 'drive_mode'),
  )


class ReadGPIOPacket(CFA635Packet):
  TYPE = 35
  FORMAT = (
    ('B', 'index'),
  ) # XXX TODO


### The display

class CFA635Display(Generic.SerialCharacterDisplay):

  # These characters do not correspond to their ASCII codes
  _TRANSLATION_TABLE = string.maketrans(r'[\]{|<=>_$',
      '\xfa\xfb\xfc\xfd\xfe\x3c\x3d\x3e\xc4\xa2')

  def __init__(self, port, baudrate=115200):
    Generic.SerialCharacterDisplay.__init__(self, port, baudrate)
    self._logger = logging.getLogger('cfa-635')
    self._backlight_amt = 0
    self._out_packets = Queue.Queue()

  ### Local helpers

  def _ValidatePosition(self, row, col):
    if row < 0 or row >= self.rows():
      raise Generic.InvalidPositionError, "Row value out of range"
    if col < 0 or col >= self.cols():
      raise Generic.InvalidPositionError, "Column value out of range"

  def _SetBacklight(self, amt):
    if int(amt) != self._backlight_amt:
      self._backlight_amt = amt
      self._WritePacket(SetBacklightPacket(amount=amt))

  def _WritePacket(self, packet):
    data = packet.Pack()
    self._logger.debug('Writing packet bytes: %s' % repr(data))
    self._serial_handle.write(data)
    self._DrainPackets()

  def _DrainPackets(self):
    timeout = 0.250
    while True:
      res = self._WaitForPacket(timeout=timeout)
      if not res:
        break
      self._HandleIncomingPacket(res)
      timeout = 0

  def _WaitForPacket(self, timeout=0.250):
    self._logger.debug('Waiting for packet timeout=%f' % timeout)
    rr, _, _ = select.select([self._serial_handle], [], [], timeout)
    if rr:
      return self._ReadPacket()
    else:
      self._logger.error('No response!')

  def _HandleIncomingPacket(self, packet):
    self._logger.debug('Got packet: %s' % packet)

  def _ReadPacket(self):
    command, data_length = struct.unpack('BB', self._serial_handle.read(2))
    command_type = command >> 6
    command_value = command & 0x3f

    if data_length > 22:
      self._logger.error('Invalid data length: %i' % data_length)
      return

    self._logger.debug('Response: %x %x %x' % (command_type, command_value, data_length))
    bytes = self._serial_handle.read(data_length)
    crc = self._serial_handle.read(2)

    return bytes

  ### IGenericDisplay interface

  def rows(self):
    return 4

  def cols(self):
    return 20

  def ClearScreen(self):
    self._WritePacket(ClearScreenPacket())

  def BacklightEnable(self, enable):
    if enable:
      self._SetBacklight(100)
    else:
      self._SetBacklight(0)

  def SetCursor(self, row, col):
    self._WritePacket(SetCursorPosPacket(col=col, row=row))

  def WriteData(self, data, row, col):
    self._logger.debug('Writing data: %s' % data)
    outstr = data.translate(self._TRANSLATION_TABLE)
    self._WritePacket(WriteDataPacket(col=col, row=row, data=outstr))

  def WriteScreen(self, buf):
    for i in xrange(self.rows()):
      start = i*self.cols()
      end = start+self.cols()
      self.WriteData(data=buf[start:end].tostring(), row=i, col=0)

  ### Nonstandard public functions
  def Reset(self):
    """Clear the screen, reset cursor, and enable backlight"""
    self.ClearScreen()
    self.EnableBacklight(True)
    self.SetCursor(0, 0)
