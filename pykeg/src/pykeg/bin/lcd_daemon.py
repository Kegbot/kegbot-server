#!/usr/bin/env python
#
# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

"""Kegbot LCD daemon."""

from pykeg.core import importhacks

import gflags
import Queue
import sys

from pykeg.core import kb_app
from pykeg.core import units
from pykeg.core import util
from pykeg.core.net import kegnet
from pykeg.core.net import kegnet_pb2

try:
  import lcdui
except ImportError:
  print>>sys.stderr, "Error: lcdui could not be imported."
  print>>sys.stderr, "(Try: sudo easy_install --upgrade pylcdui)"
  sys.exit(1)

from lcdui.ui import frame
from lcdui.ui import ui
from lcdui.ui import widget

DEVICE_CFA_635 = 'cfa635'
DEVICE_MTXORB = 'mtxorb20x4'

DEVICE_CHOICES = ', '.join((
  DEVICE_CFA_635,
  DEVICE_MTXORB
))

FLAGS = gflags.FLAGS

gflags.DEFINE_string('lcd_device_path', '/dev/ttyUSB0',
    'Path to lcd device file.')

gflags.DEFINE_integer('lcd_baud_rate', 115200,
    'LCD baud rate.')

gflags.DEFINE_integer('backlight_timeout', 300,
    'Number of seconds of inactivity before LCD backlight will be disabled.')

gflags.DEFINE_string('lcd_device_type', DEVICE_CFA_635,
    'Type of LCD device. Choices are: %s' % DEVICE_CHOICES)


class KegUi:
  STATE_MAIN = 'main'
  STATE_POUR = 'pour'

  def __init__(self, path=None):
    if not path:
      path = FLAGS.lcd_device_path

    if FLAGS.lcd_device_type == DEVICE_CFA_635:
      from lcdui.devices import CrystalFontz
      self._lcdobj = CrystalFontz.CFA635Display(path, FLAGS.lcd_baud_rate)
    elif FLAGS.lcd_device_type == DEVICE_MTXORB:
      from lcdui.devices import MatrixOrbital
      self._lcdobj = MatrixOrbital.MatrixOrbitalDisplay(path,
          FLAGS.lcd_baud_rate)
    else:
      raise ValueError, "Bad device type: %s" % FLAGS.lcd_device_type

    self._lcdui = ui.LcdUi(self._lcdobj, FLAGS.backlight_timeout)
    self._last_flow_status = None

    self._main_frame = self._GetMainFrame()
    self._pour_frame = self._GetPourFrame()

    self._flow_status_by_tap = {}

    self._frames = {
      'main': self._main_frame,
      'pour': self._pour_frame,
    }

    self._state = None
    self._SetState(self.STATE_MAIN)

  def _GetMainFrame(self):
    f = self._lcdui.FrameFactory(frame.Frame)

    f.BuildWidget(widget.LineWidget,
        contents=' ================== ', row=0, col=0)
    f.BuildWidget(widget.LineWidget,
        contents='       kegbot!      ', row=1, col=0)
    f.BuildWidget(widget.LineWidget,
        contents='      beer you.     ', row=2, col=0)
    f.BuildWidget(widget.LineWidget,
        contents=' ================== ', row=3, col=0)

    return f

  def _GetPourFrame(self):
    f = self._lcdui.FrameFactory(frame.Frame)
    f.BuildWidget(widget.LineWidget, name='line0',
        contents='_now pouring________', row=0, col=0)
    f.BuildWidget(widget.LineWidget, name='user',
        prefix='|user: ', row=1, col=0)
    f.BuildWidget(widget.LineWidget, name='ounces',
        prefix='|oz: ', row=2, col=0)
    f.BuildWidget(widget.LineWidget, name='line3',
        contents='|                   ', row=3, col=0)
    return f

  def _UpdateFromFlow(self, flow_update):
    f = self._pour_frame
    user_widget = f.GetWidget('user')
    user_widget.set_contents(str(flow_update.username))

    amt = units.Quantity(flow_update.volume_ml, units.UNITS.Milliliter)
    ounces = amt.ConvertTo.Ounce

    ounces_widget = f.GetWidget('ounces')
    ounces_widget.set_contents('%.2f' % ounces)

  def HandleFlowStatus(self, event):
    tap_name = event.tap_name
    last_status = self._flow_status_by_tap.get(tap_name)
    self._flow_status_by_tap[tap_name] = event

    self._lcdui.Activity()

    if event.state == event.COMPLETED:
      self._SetState(self.STATE_MAIN)
    else:
      self._SetState(self.STATE_POUR)
      self._UpdateFromFlow(event)

  def _SetState(self, state):
    if state == self._state:
      return

    self._state = state

    if self._state == self.STATE_MAIN:
      self._lcdui.SetFrame(self._main_frame)
    elif self._state == self.STATE_POUR:
      self._lcdui.SetFrame(self._pour_frame)

  def MainLoop(self):
    return self._lcdui.MainLoop()


class LcdDaemonApp(kb_app.App):
  def __init__(self, name='lcd_daemon'):
    kb_app.App.__init__(self, name)

  def _Setup(self):
    kb_app.App._Setup(self)
    kb_lcdui = KegUi()
    self._AddAppThread(LcdUiThread('kb-lcdui', kb_lcdui))
    self._AddAppThread(KegnetMonitorThread('kegnet-monitor', kb_lcdui))


class LcdUiThread(util.KegbotThread):
  def __init__(self, name, ui):
    util.KegbotThread.__init__(self, name)
    self._lcdui = ui

  def ThreadMain(self):
    self._logger.info('Starting main loop.')
    self._lcdui.MainLoop()
    self._logger.info('Exited main loop.')


class LcdKegnetClient(kegnet.SimpleKegnetClient):
  def __init__(self, kb_lcdui, addr=FLAGS.kb_core_addr):
    kegnet.KegnetClient.__init__(self, addr)
    self._kb_lcdui = kb_lcdui

  def onFlowUpdate(self, event):
    self._kb_lcdui.HandleFlowStatus(event)


class KegnetMonitorThread(util.KegbotThread):
  def __init__(self, name, kb_lcdui):
    util.KegbotThread.__init__(self, name)
    self._kb_lcdui = kb_lcdui
    self._client = LcdKegnetClient(self._kb_lcdui)

  def ThreadMain(self):
    self._logger.info('Starting main loop.')
    while not self._quit:
      self._client.serve_forever()
    self._client.stop()


if __name__ == '__main__':
  LcdDaemonApp.BuildAndRun()
