#!/usr/bin/env python
#
# Copyright 2003-2009 Mike Wakerly <opensource@hoho.com>
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

"""Kegbot Core Application.

This is the Kegbot Core application, which runs the main drink recording and
post-processing loop. There is exactly one instance of a kegbot core per kegbot
system.

For more information, please see the kegbot documentation.
"""

import logging
import time
import warnings
warnings.simplefilter("ignore", DeprecationWarning)

import gflags

from pykeg.core import alarm
from pykeg.core import backend
from pykeg.core import kbevent
from pykeg.core import kb_app
from pykeg.core import kb_threads
from pykeg.core import manager
from pykeg.core.net import kegnet

FLAGS = gflags.FLAGS

gflags.DEFINE_boolean('web_backend', False,
    'If true, uses the web backend implementation rather than a database connection.')

class KegbotEnv(object):
  """ A class that wraps the context of the kegbot core.

  An instance of this class owns all the threads and services used in the kegbot
  core. It is commonly passed around to objects that the core creates.
  """
  def __init__(self):
    self._event_hub = kbevent.EventHub()
    self._logger = logging.getLogger('env')

    self._kegnet_server = kegnet.KegnetServer(name='kegnet', kb_env=self,
        addr=FLAGS.kb_core_bind_addr)

    if FLAGS.web_backend:
      # Web backend.
      self._logger.info('Using web backend: %s' % FLAGS.api_url)
      self._backend = backend.WebBackend()
    else:
      # Database backend.
      self._logger.info('Using database backend.')
      self._backend = backend.KegbotBackend()

    # Build managers
    self._alarm_manager = alarm.AlarmManager()
    self._tap_manager = manager.TapManager('tap-manager', self._event_hub)
    self._flow_manager = manager.FlowManager('flow-manager', self._event_hub,
        self._tap_manager)
    self._authentication_manager = manager.AuthenticationManager('auth-manager',
        self._event_hub, self._flow_manager, self._tap_manager, self._backend)
    self._drink_manager = manager.DrinkManager('drink-manager', self._event_hub,
        self._backend)
    self._thermo_manager = manager.ThermoManager('thermo-manager',
        self._event_hub, self._backend)
    self._subscription_manager = manager.SubscriptionManager('pubsub',
        self._event_hub, self._kegnet_server)

    # Build threads
    self._threads = set()
    self._service_thread = kb_threads.EventHandlerThread(self, 'service-thread')
    self._service_thread.AddEventHandler(self._tap_manager)
    self._service_thread.AddEventHandler(self._flow_manager)
    self._service_thread.AddEventHandler(self._drink_manager)
    self._service_thread.AddEventHandler(self._thermo_manager)
    self._service_thread.AddEventHandler(self._authentication_manager)
    self._service_thread.AddEventHandler(self._subscription_manager)

    self.AddThread(self._service_thread)

    self.AddThread(kb_threads.EventHubServiceThread(self, 'eventhub-thread'))
    self.AddThread(kb_threads.NetProtocolThread(self, 'net-thread'))
    self.AddThread(kb_threads.AlarmManagerThread(self, 'alarmmanager-thread'))
    self.AddThread(kb_threads.HeartbeatThread(self, 'heartbeat-thread'))

    self._watchdog_thread = kb_threads.WatchdogThread(self, 'watchdog-thread')
    self.AddThread(self._watchdog_thread)

    for tap in self._backend.GetAllTaps():
      # TODO: get rid of max_tick_delta parameter entirely
      self._tap_manager.RegisterTap(tap.meter_name, tap.ml_per_tick,
          (1/tap.ml_per_tick*500))

  def AddThread(self, thr):
    self._threads.add(thr)
    if isinstance(thr, kb_threads.CoreThread):
      self.GetEventHub().AddListener(thr)

  def GetWatchdogThread(self):
    return self._watchdog_thread

  def GetAlarmManager(self):
    return self._alarm_manager

  def GetBackend(self):
    return self._backend

  def GetKegnetServer(self):
    return self._kegnet_server

  def GetEventHub(self):
    return self._event_hub

  def GetTapManager(self):
    return self._tap_manager

  def GetFlowManager(self):
    return self._flow_manager

  def GetAuthenticationManager(self):
    return self._authentication_manager

  def GetThreads(self):
    return self._threads


class KegbotCoreApp(kb_app.App):
  def __init__(self, name='core'):
    kb_app.App.__init__(self, name)
    self._env = KegbotEnv()

  def _MainLoop(self):
    event = kbevent.StartCompleteEvent()
    self._env.GetEventHub().PublishEvent(event)
    watchdog = self._env.GetWatchdogThread()
    while not self._do_quit:
      try:
        watchdog.join(1)
        if not watchdog.isAlive():
          self._logger.error("Watchdog thread exited, quitting")
          self.Quit()
          return
      except KeyboardInterrupt:
        self._logger.info("Got keyboard interrupt, quitting")
        self.Quit()
        return

  def _Setup(self):
    kb_app.App._Setup(self)
    for thr in self._env.GetThreads():
      self._AddAppThread(thr)

  def Quit(self):
    self._do_quit = True
    event = kbevent.QuitEvent()
    self._env.GetEventHub().PublishEvent(event)
    time.sleep(1.0)

    self._logger.info('Stopping any remaining threads')
    self._StopThreads()
    self._logger.info('Kegbot stopped.')
    self._TeardownLogging()

