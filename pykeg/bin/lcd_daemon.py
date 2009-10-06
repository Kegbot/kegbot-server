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

"""Kegbot LCD daemon."""

import importhacks

import serial
import time

from pykeg.core import kb_app
from pykeg.core import units
from pykeg.core import util
from pykeg.core.net import kegnet_client
from pykeg.external.gflags import gflags

from lcdui.devices import CrystalFontz
from lcdui.ui import frame
from lcdui.ui import ui
from lcdui.ui import widget

FLAGS = gflags.FLAGS

gflags.DEFINE_string('lcd_device_path', '/dev/ttyUSB0',
    'Path to lcd device file.')


class KegUi:
  STATE_MAIN = 'main'
  STATE_POUR = 'pour'

  def __init__(self, path=FLAGS.lcd_device_path):
    self._lcdobj = CrystalFontz.CFA635Display(path)
    self._lcdui = ui.LcdUi(self._lcdobj)
    self._last_flow_status = None

    self._main_frame = self._GetMainFrame()
    self._pour_frame = self._GetPourFrame()

    self._frames = {
      'main': self._main_frame,
      'pour': self._pour_frame,
    }

    self._state = None
    self._SetState(self.STATE_MAIN)

  def _GetMainFrame(self):
    f = self._lcdui.FrameFactory(frame.Frame)
    f.AddWidget('line0',
        widget.LineWidget(contents=' ================== '),
        row=0, col=0)
    f.AddWidget('line1',
        widget.LineWidget(contents='       kegbot!      '),
        row=1, col=0)
    f.AddWidget('line2',
        widget.LineWidget(contents='      beer you.     '),
        row=2, col=0)
    f.AddWidget('line3',
        widget.LineWidget(contents=' ================== '),
        row=3, col=0)
    return f

  def _GetPourFrame(self):
    f = self._lcdui.FrameFactory(frame.Frame)
    f.AddWidget('line0',
        widget.LineWidget(contents='_now pouring________'),
        row=0, col=0)
    f.AddWidget('user',
        widget.LineWidget(prefix='|user: '),
        row=1, col=0)
    f.AddWidget('ounces',
        widget.LineWidget(prefix='|oz: '),
        row=2, col=0)
    f.AddWidget('line3',
        widget.LineWidget(contents='|                   '),
        row=3, col=0)
    return f

  def _UpdateFromFlow(self, status):
    f = self._pour_frame
    user_widget = f.GetWidget('user')
    user_widget.set_contents(str(status.user))

    amt = units.Quantity(status.volume_ml, units.UNITS.Milliliter)
    ounces = amt.ConvertTo.Ounce

    ounces_widget = f.GetWidget('ounces')
    ounces_widget.set_contents('%.2f' % ounces)

  def HandleFlowStatus(self, status):
    # TODO(mikey): kegnet cleanup
    if status and status.ticks is None:
      status = None

    if status != self._last_flow_status:
      if not status or status.ticks is None:
        self._SetState(self.STATE_MAIN)
        return

    self._last_flow_status = status
    self._lcdui.Activity()
    self._SetState(self.STATE_POUR)
    if status:
      self._UpdateFromFlow(status)

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
  def __init__(self, name='lcd_daemon', daemon=FLAGS.daemon):
    kb_app.App.__init__(self, name, daemon)

  def _Setup(self):
    kb_app.App._Setup(self)
    kb_lcdui = KegUi()
    self._AddAppThread(LcdUiThread('kb-lcdui', kb_lcdui))
    self._AddAppThread(KegnetMonitorThread('kegnet-monitor', kb_lcdui))


class LcdUiThread(util.KegbotThread):
  def __init__(self, name, ui):
    util.KegbotThread.__init__(self, name)
    self._lcdui = ui

  def run(self):
    self._logger.info('Starting main loop.')
    self._lcdui.MainLoop()
    self._logger.info('Exited main loop.')


class KegnetMonitorThread(util.KegbotThread):
  def __init__(self, name, kb_lcdui):
    util.KegbotThread.__init__(self, name)
    self._client = kegnet_client.KegnetClient()
    self._kb_lcdui = kb_lcdui

  def run(self):
    self._logger.info('Starting main loop.')
    while not self._quit:
      # TODO(mikey): kegnet sorely needs an event-driven api, this polling
      # sucks...
      flow_status = self._client.GetFlowStatus('flow0')
      self._kb_lcdui.HandleFlowStatus(flow_status)
      if flow_status:
        time.sleep(0.5)
      else:
        time.sleep(2.0)
    self._logger.info('Exiting main loop.')


if __name__ == '__main__':
  LcdDaemonApp.BuildAndRun()
