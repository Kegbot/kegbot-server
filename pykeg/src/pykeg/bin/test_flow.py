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

"""A Kegnet client that sends a fake flow."""

from pykeg.core import importhacks

import gflags
import math
import time

from pykeg.core import kb_app
from pykeg.core import kb_common
from pykeg.core import util
from pykeg.core.net import kegnet

FLAGS = gflags.FLAGS

gflags.DEFINE_integer('ticks', 1000,
    'Number of ticks to send.',
    lower_bound=1)

gflags.DEFINE_integer('steps', 10,
    'Number of updates to send --ticks.  In other words, '
    'the value of `ticks/steps` will be sent `steps` times.',
    lower_bound=1)

gflags.DEFINE_float('delay_seconds', 0.1,
    'Delay, in seconds, between meter updates.  If set to '
    '0, there will be no delay.',
    lower_bound=0, upper_bound=60)

gflags.DEFINE_string('auth_token', '',
    'If specified, sends auth_device|token as attached.')

gflags.DEFINE_boolean('explicit_start_stop', False,
    'If true, the Kegnet client should send explicit flow '
    'start and stop requests.  This is not strictly required. '
    'Setting to False will cause the flow to end when the core '
    'has detected it as idle.')

class SmoothFlow:
  def __init__(self, num_ticks, num_steps):
    self._total_ticks = num_ticks
    self._step_amt = int(math.ceil(float(num_ticks) / float(num_steps)))

  def __iter__(self):
    reading = 0
    yield reading
    while reading < self._total_ticks:
      remain = (self._total_ticks - reading)
      inc = min(self._step_amt, remain)
      reading += inc
      yield reading


class FakeKegboardApp(kb_app.App):
  def _Setup(self):
    kb_app.App._Setup(self)
    self._asyncore_thread = util.AsyncoreThread('asyncore')
    self._AddAppThread(self._asyncore_thread)

  def _MainLoop(self):
    client = kegnet.KegnetClient()
    connected = client.Reconnect()
    if not connected:
      self._logger.error('Could not connect to core.')
      return
    flow = SmoothFlow(FLAGS.ticks, FLAGS.steps)

    try:
      auth_device, token_value = FLAGS.auth_token.split('|')
    except ValueError:
      auth_device, token_value = None, None

    if auth_device and token_value:
      client.SendAuthTokenAdd(FLAGS.tap_name, auth_device, token_value)
      client.SendAuthTokenRemove(FLAGS.tap_name, auth_device, token_value)
      client.SendAuthTokenAdd(FLAGS.tap_name, auth_device, token_value)

    if FLAGS.explicit_start_stop:
      client.SendFlowStart(FLAGS.tap_name)

    for amt in flow:
      self._logger.info('Sending flow update: %i' % amt)
      client.SendMeterUpdate(FLAGS.tap_name, amt)
      if FLAGS.delay_seconds:
        time.sleep(FLAGS.delay_seconds)

    if auth_device and token_value:
      client.SendAuthTokenRemove(FLAGS.tap_name, auth_device, token_value)

    if FLAGS.explicit_start_stop:
      client.SendFlowStop(FLAGS.tap_name)

    client.close_when_done()
    time.sleep(3.0)

if __name__ == '__main__':
  FakeKegboardApp.BuildAndRun(name='test_flow')
