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

"""Simple kegboard monitor program.

This app attaches to a kegboard and prints all packets it receives.
"""

from pykeg.core import importhacks

import os

import gflags
import serial

from pykeg.core import kb_app
from pykeg.hw.kegboard import kegboard

FLAGS = gflags.FLAGS


class KegboardMonitorApp(kb_app.App):

  def _SetupSerial(self):
    self._logger.info('Setting up serial port...')
    self._serial_fd = serial.Serial(FLAGS.kegboard_device, FLAGS.kegboard_speed)
    self._reader = kegboard.KegboardReader(self._serial_fd)

  def _MainLoop(self):
    self._SetupSerial()
    self._logger.info('Starting reader loop...')
    ping_message = kegboard.PingCommand()
    self._serial_fd.write(ping_message.ToBytes())
    while not self._do_quit:
      try:
        msg = self._reader.GetNextMessage()
        print msg
      except:
        break
    self._serial_fd.close()
    self._logger.info('Reader loop ended.')


if __name__ == '__main__':
  KegboardMonitorApp.BuildAndRun()
