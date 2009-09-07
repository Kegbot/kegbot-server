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
import signal
import sys
import time

from pykeg.core import alarm
from pykeg.core import backend
from pykeg.core import event
from pykeg.core import kb_app
from pykeg.core import kb_common
from pykeg.core import kb_threads
from pykeg.core import manager
from pykeg.core import service
from pykeg.external.gflags import gflags

FLAGS = gflags.FLAGS

class KegbotEnv(object):
  """ A class that wraps the context of the kegbot core.

  An instance of this class owns all the threads and services used in the kegbot
  core. It is commonly passed around to objects that the core creates.
  """
  def __init__(self):
    self._event_hub = event.EventHub()

    # Build managers and services
    self._alarm_manager = alarm.AlarmManager()
    self._tap_manager = manager.TapManager()
    self._flow_manager = manager.FlowManager(self._tap_manager)
    self._authentication_manager = manager.AuthenticationManager()

    self._drink_db_service = service.DrinkDatabaseService('drink_db_service', self)
    self._flow_service = service.FlowManagerService('flow_service', self)
    self._thermo_service = service.ThermoService('thermo_service', self)

    self._backend = backend.KegbotBackend()
    self._backend.CheckSchemaVersion()

    # Build threads
    self._threads = set()
    self._service_thread = kb_threads.EventHandlerThread(self, 'service-thread')
    self._service_thread.AddService(self._flow_service)
    self._service_thread.AddService(self._drink_db_service)
    self._service_thread.AddService(self._thermo_service)

    if self._backend.GetConfig().IsFeatureEnabled('twitter'):
      from pykeg.contrib.twitter import service as twitter_service
      self._twitter_service = twitter_service.TwitterService('twitter', self)
      self._service_thread.AddService(self._twitter_service)

    self.AddThread(self._service_thread)

    self.AddThread(kb_threads.EventHubServiceThread(self, 'eventhub-thread'))
    self.AddThread(kb_threads.NetProtocolThread(self, 'net-thread'))
    self.AddThread(kb_threads.AlarmManagerThread(self, 'alarmmanager-thread'))
    self.AddThread(kb_threads.FlowMonitorThread(self, 'flowmonitor-thread'))

    self._watchdog_thread = kb_threads.WatchdogThread(self, 'watchdog-thread')
    self.AddThread(self._watchdog_thread)

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
  def __init__(self, name='core', daemon=FLAGS.daemon):
    kb_app.App.__init__(self, name, daemon)
    self._env = KegbotEnv()

  def _MainLoop(self):
    self._env.GetEventHub().PublishEvent(kb_common.KB_EVENT.START_COMPLETE)
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
    self._env.GetEventHub().PublishEvent(kb_common.KB_EVENT.QUIT)
    time.sleep(1.0)

    self._logger.info('Stopping any remaining threads')
    self._StopThreads()
    self._logger.info('Kegbot stopped.')
    self._TeardownLogging()

