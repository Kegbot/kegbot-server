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
exchange data.  The address and port of the core is specified with the flags
--kb_core_hostname and --kb_core_port.
"""

import Queue
import asyncore
import asynchat
import socket
import cStringIO
import logging
import sys

import serial

from pykeg.core import kb_app
from pykeg.core import kb_common
from pykeg.core import util
from pykeg.core.net import kegnet
from pykeg.hw.kegboard import kegboard
from pykeg.external.gflags import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_string('kegboard_device', '/dev/ttyUSB0',
    'An explicit device file (eg /dev/ttyUSB0) on which to listen for kegboard '
    'packets.  This mechanism can be used in addtion to (or instead of) the '
    '--use_udev feature.)')

gflags.DEFINE_integer('kegboard_speed', 115200,
    'Baud rate of --kegboard_device')

gflags.DEFINE_string('kegboard_name', 'mykegboard',
    'Name to use for this kegboard.')

gflags.DEFINE_string('kb_core_hostname', 'localhost',
    'Hostname or ip address of the kegbot core to connect to.  If the special '
    'value "_auto_" is given (default), the program will attempt to locate '
    'the kegbot core automatically. ')

gflags.DEFINE_integer('kb_core_port', 9999,
    'Port number of host at --kb_core_hostname to connect to.  Note that this '
    'value is ignored if --kb_core_hostname=_auto_.')


class KegboardManagerApp(kb_app.App):
  def __init__(self, name='core', daemon=FLAGS.daemon):
    kb_app.App.__init__(self, name, daemon)

  def _Setup(self):
    kb_app.App._Setup(self)

    net_addr = (FLAGS.kb_core_hostname, FLAGS.kb_core_port)
    client = kegnet.KegnetClient(net_addr, FLAGS.kegboard_name)

    self._network_thr = KegboardNetworkThread('network', FLAGS.kegboard_name,
        client)
    self._AddAppThread(self._network_thr)

    self._manager_thr = KegboardManagerThread('kegboard-manager',
        self._network_thr)
    self._AddAppThread(self._manager_thr)

    self._device_io_thr = KegboardDeviceIoThread('device-io', self._manager_thr,
        FLAGS.kegboard_name, FLAGS.kegboard_device, FLAGS.kegboard_speed)
    self._AddAppThread(self._device_io_thr)


class KegboardManagerThread(util.KegbotThread):
  """Manager of local kegboard devices."""

  def __init__(self, name, net_thread):
    util.KegbotThread.__init__(self, name)
    self._net_thread = net_thread
    self._message_queue = Queue.Queue()

    self._meter_cache = {}

  def PostDeviceMessage(self, device_name, device_message):
    """Receive a message from a device, for processing."""
    self._message_queue.put((device_name, device_message))

  def run(self):
    self._logger.info('Starting main loop.')
    while not self._quit:
      try:
        device_name, device_message = self._message_queue.get(timeout=1.0)
      except Queue.Empty:
        continue
      self._HandleDeviceMessage(device_name, device_message)
    self._logger.info('Exiting main loop.')

  def _HandleDeviceMessage(self, device_name, msg):
    client = self._net_thread.GetClient(device_name)

    if isinstance(msg, kegboard.MeterStatusMessage):
      # Flow update: compare to last value and send a message if needed
      meter_name = msg.meter_name.GetValue()
      curr_val = msg.meter_reading.GetValue()
      last_val = self._meter_cache.get(meter_name)
      if last_val is None or curr_val > last_val:
        client.FlowUpdate(meter_name, curr_val)
      self._meter_cache[meter_name] = curr_val
    elif isinstance(msg, kegboard.TemperatureReadingMessage):
      # Thermo update
      #client.SendThermoStatus(msg.sensor_name.GetValue(),
      #    msg.sensor_reading.GetValue())
      pass


class KegboardDeviceIoThread(util.KegbotThread):
  """Manages all device I/O.

  This thread continuously reads from attached kegboard devices and passes
  messages to the KegboardManagerThread.
  """
  def __init__(self, name, manager, device_name, device_path, device_speed):
    util.KegbotThread.__init__(self, name)
    self._manager = manager
    self._device_name = device_name
    self._device_path = device_path
    self._device_speed = device_speed

    self._reader = None
    self._serial_fd = None

  def _SetupSerial(self):
    self._logger.info('Setting up serial port...')
    self._serial_fd = serial.Serial(self._device_path, self._device_speed)
    self._reader = kegboard.KegboardReader(self._serial_fd, self._device_name)

  def run(self):
    self._SetupSerial()
    try:
      self._MainLoop()
    finally:
      self._serial_fd.close()

  def _MainLoop(self):
    self._logger.info('Starting reader loop...')
    while not self._quit:
      msg = self._reader.GetNextMessage()
      self._manager.PostDeviceMessage(self._device_name, msg)
    self._logger.info('Reader loop ended.')


class KegboardNetworkThread(util.KegbotThread):
  """ Object that connects a kegboard stream to a KegnetProtocolClient. """
  def __init__(self, name, device_name, client):
    util.KegbotThread.__init__(self, name)
    self._device_name = device_name
    self._sock_map = {}
    self._client = client

  def _Register(self):
    self._logger.info("Registering device.")
    self._client.Login()

  def GetClient(self, device_name):
    return self._client

  def run(self):
    self._Register()
    self._logger.info("Running asyncore loop.")
    asyncore.loop(map=self._sock_map)


if __name__ == '__main__':
  KegboardManagerApp.BuildAndRun()
