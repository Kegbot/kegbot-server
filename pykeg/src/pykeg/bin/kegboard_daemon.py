#!/usr/bin/env python
#
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

"""Kegboard daemon.

The kegboard daemon is the primary interface between a kegboard devices and a
kegbot system.  The process is responsible for several tasks, including:
  - discovering kegboards available locally
  - connecting to the kegbot core and registering the individual boards
  - accumulating data if the kegbot core is offline

The kegboard daemon is compatible with any device that speaks the Kegboard
Serial Protocol. See http://kegbot.org/docs for the complete specification.

The daemon should run on any machine which is attached to kegboard hardware.

The daemon must connect to a Kegbot Core in order to publish data (such as flow
and temperature events).  This is a TCP connection, using the Kegnet Protocol to
exchange data.
"""

import Queue

import gflags
import serial

from pykeg.core import importhacks
from pykeg.core import kb_app
from pykeg.core import kb_common
from pykeg.core import util
from pykeg.core.net import kegnet
from pykeg.hw.kegboard import kegboard

FLAGS = gflags.FLAGS

gflags.DEFINE_string('kegboard_name', 'kegboard',
    'Name of this kegboard that will be used when talking to the core. '
    'If you are using multiple kegboards, you will want to run different '
    'daemons with different names. Otherwise, the default is fine.')

gflags.DEFINE_boolean('show_messages', True,
    'Print all messages going to and from the kegboard. Useful for '
    'debugging.')

gflags.DEFINE_integer('required_firmware_version', 4,
    'Minimum firmware version required.  If the device has an older '
    'firmware version, the daemon will refuse to service it.  This '
    'value should probably not be changed.')

class KegboardKegnetClient(kegnet.SimpleKegnetClient):
  pass

class KegboardManagerApp(kb_app.App):
  def __init__(self, name='core'):
    kb_app.App.__init__(self, name)

  def _Setup(self):
    kb_app.App._Setup(self)

    self._client = KegboardKegnetClient()

    self._client_thr = kegnet.KegnetClientThread('kegnet', self._client)
    self._AddAppThread(self._client_thr)

    self._manager_thr = KegboardManagerThread('kegboard-manager',
        self._client)
    self._AddAppThread(self._manager_thr)

    self._device_io_thr = KegboardDeviceIoThread('device-io', self._manager_thr,
        FLAGS.kegboard_device, FLAGS.kegboard_speed)
    self._AddAppThread(self._device_io_thr)


class KegboardManagerThread(util.KegbotThread):
  """Manager of local kegboard devices."""

  def __init__(self, name, client):
    util.KegbotThread.__init__(self, name)
    self._client = client
    self._message_queue = Queue.Queue()

  def _DeviceName(self, base_name):
    return '%s.%s' % (FLAGS.kegboard_name, base_name)

  def PostDeviceMessage(self, device_name, device_message):
    """Receive a message from a device, for processing."""
    self._message_queue.put((device_name, device_message))

  def run(self):
    self._logger.info('Starting main loop.')
    initialized = False

    while not self._quit:
      try:
        device_name, device_message = self._message_queue.get(timeout=1.0)
      except Queue.Empty:
        continue

      if FLAGS.show_messages:
        self._logger.info('RX: %s' % str(device_message))
      self._HandleDeviceMessage(device_name, device_message)

    self._logger.info('Exiting main loop.')

  def _HandleDeviceMessage(self, device_name, msg):
    if isinstance(msg, kegboard.MeterStatusMessage):
      meter_name = self._DeviceName(msg.meter_name)
      curr_val = msg.meter_reading
      self._client.SendMeterUpdate(meter_name, curr_val)

    elif isinstance(msg, kegboard.TemperatureReadingMessage):
      sensor_name = self._DeviceName(msg.sensor_name)
      sensor_value = msg.sensor_reading
      self._client.SendThermoUpdate(sensor_name, sensor_value)

    elif isinstance(msg, kegboard.OnewirePresenceMessage):
      strval = '%016x' % msg.device_id
      if msg.status == 1:
        self._client.SendAuthTokenAdd(FLAGS.tap_name,
            kb_common.AUTH_MODULE_CORE_ONEWIRE, strval)
      else:
        self._client.SendAuthTokenRemove(FLAGS.tap_name,
            kb_common.AUTH_MODULE_CORE_ONEWIRE, strval)


class KegboardDeviceIoThread(util.KegbotThread):
  """Manages all device I/O.

  This thread continuously reads from attached kegboard devices and passes
  messages to the KegboardManagerThread.
  """
  def __init__(self, name, manager, device_path, device_speed):
    util.KegbotThread.__init__(self, name)
    self._manager = manager
    self._device_path = device_path
    self._device_speed = device_speed
    self._reader = None
    self._serial_fd = None

  def _SetupSerial(self):
    self._logger.info('Setting up serial port...')
    self._serial_fd = serial.Serial(self._device_path, self._device_speed)
    self._reader = kegboard.KegboardReader(self._serial_fd)

  def run(self):
    self._SetupSerial()
    try:
      self._MainLoop()
    finally:
      self._serial_fd.close()

  def Ping(self):
    ping_message = kegboard.PingCommand()
    self._reader.WriteMessage(ping_message)

  def _MainLoop(self):
    self._logger.info('Starting reader loop...')

    # Ping the board a couple of times before going into the listen loop.
    for i in xrange(2):
      self.Ping()

    initialized = False
    while not self._quit:
      msg = self._reader.GetNextMessage()

      # Check the reported firmware version. If it is not acceptable, then
      # drop all messages until it is updated.
      # TODO(mikey): kill the application when this happens? It isn't strictly
      # necessary, but is probably the most obvious way to get the point across.
      if isinstance(msg, kegboard.HelloMessage):
        version = msg.firmware_version
        if version >= FLAGS.required_firmware_version:
          if not initialized:
            self._logger.info('Found a Kegboard! Firmware version %i' % version)
            initialized = True
        else:
          self._logger.error('Attached kegboard firmware version (%s) is '
              'less than the required version (%s); please update this '
              'kegboard.' % (actual, required))
          self._logger.warning('Messages from this board will be ignored '
              'until it is updated.')
          initialized = False

      if not initialized:
        self.Ping()
        time.sleep(0.1)
        continue

      self._manager.PostDeviceMessage('kegboard', msg)
    self._logger.info('Reader loop ended.')


if __name__ == '__main__':
  KegboardManagerApp.BuildAndRun()
