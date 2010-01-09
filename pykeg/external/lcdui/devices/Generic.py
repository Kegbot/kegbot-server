import serial

from lcdui.devices import Interfaces

class InvalidPositionError(Exception):
  """Raised when a command was attempted on an out-of-range location"""


class SerialCharacterDisplay(Interfaces.ICharacterDisplay):
  """A character display that is driven by a serial port."""
  def __init__(self, port, baudrate=115200):
    self._serial_handle = serial.Serial(port=port, baudrate=baudrate)


class MockCharacterDisplay(Interfaces.ICharacterDisplay):
  def __init__(self, rows, cols):
    self._rows = rows
    self._cols = cols
    self._contents = self._AllocContents()

  def _AllocContents(self):
    return " " * (self._rows * self._cols)

  def ClearScreen(self):
    self._contents = self._AllocContents()

  def BacklightEnable(self, enable):
    pass

  def rows(self):
    return self._rows

  def cols(self):
    return self._cols

  def WriteScreen(self, buf):
    self._contents = buf
    ret = ""
    for i in xrange(self._rows):
      ret += "|" + self._contents[i*self._cols:(i+1)*self._cols].tostring() + "|\n"
