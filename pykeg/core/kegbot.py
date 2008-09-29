#!/usr/bin/env python
#
# Copyright 2008 Mike Wakerly <opensource@hoho.com>
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

"""Main process for the kegbot core program.

This module contains the |KegBot| class, which runs the main drink recording and
post-processing loop. There is exactly one instance of |KegBot| per kegbot
system.
"""

# standard lib imports
import itertools
import logging
import Queue
import signal
import sys
import time

# kegbot lib imports
from pykeg.core import Flow
from pykeg.core import Interfaces
from pykeg.core import kb_common
from pykeg.core import kb_threads
from pykeg.core import KegbotJsonServer
from pykeg.core import models
from pykeg.core import SQLConfigParser

from pykeg.core.Devices import Net
from pykeg.core.Devices import NoOp


# ---------------------------------------------------------------------------- #
# Main classes
# ---------------------------------------------------------------------------- #

class KegBot:
   """ the thinking kegerator! """
   def __init__(self, daemon):
      self.config = SQLConfigParser.DjangoConfigParser()
      self._is_daemon = daemon
      self._channels = []
      self._devices = []
      self._authed_users = {}
      self._do_quit = False

      # ready to perform second stage of initialization
      self._setup()
      self._setsigs()

      # start everything up
      self.MainEventLoop()

   def _setup(self):

      # initialize the config, from stored values in MySQL
      self.config.read(models.Config)

      # set up logging, using the python 2.3 logging module
      self._SetupLogging()
      self.logger = logging.getLogger('pykeg')

      # check schema freshness
      installed_schema = self.config.getint('db', 'schema_version')
      if installed_schema < models.SCHEMA_VERSION:
         self.logger.fatal('Error: outdated schema detected! (latest = %i, installed = %i)' %
               (installed_schema, models.SCHEMA_VERSION))
         self.logger.fatal('Please run scripts/updatedb.py to correct this.')
         self.logger.fatal('Aborting.')
         sys.exit(1)

      # json server
      self._json_server = KegbotJsonServer.KegbotJsonServer(
          ('', kb_common.JSON_SERVER_PORT_DEFAULT))
      self._json_server.start()
      self.AddDevice(self._json_server)

      self._flow_thread = kb_threads.FlowProcessingThread(self)
      self._flow_thread.start()

      # local hardware
      self._net_kegboard = Net.KegBoard()
      self._net_kegboard.start()

      self._channel_0 = Flow.Channel(chanid = 0,
            valve_relay = NoOp.Relay(),
            flow_meter = self._net_kegboard,
      )
      self.AddChannel(self._channel_0)

   def _setsigs(self):
      """ Sets HUP, INT, QUIT, TERM to go to cause a quit """
      signal.signal(signal.SIGHUP, self._SignalHandler)
      signal.signal(signal.SIGINT, self._SignalHandler)
      signal.signal(signal.SIGQUIT, self._SignalHandler)
      signal.signal(signal.SIGTERM, self._SignalHandler)

   def _SignalHandler(self, signum, frame):
      """ All handled signals cause a quit """
      self.Quit()

   def Quit(self):
      self.logger.info('main: attempting to quit')
      self._do_quit = True

   def AddChannel(self, chan):
      self._channels.append(chan)

   def AddDevice(self, dev):
      self._devices.append(dev)

   def _SetupLogging(self, level=logging.INFO):
      logging.root.setLevel(level)

      # add a file-output handler
      if self.config.getboolean('logging','use_logfile'):
         hdlr = logging.FileHandler(self.config.get('logging','logfile'))
         formatter = logging.Formatter(self.config.get('logging','logformat'))
         hdlr.setFormatter(formatter)
         logging.root.addHandler(hdlr)

      # add tty handler
      if not self._is_daemon:
         hdlr = logging.StreamHandler(sys.stdout)
         formatter = logging.Formatter(self.config.get('logging','logformat'))
         hdlr.setFormatter(formatter)
         logging.root.addHandler(hdlr)

   def _ProcessDevices(self):
      for dev in self._devices:
         if isinstance(dev, Interfaces.IAuthDevice):
            for username in self._NewUsersFromAuthDevice(dev):
               self.AuthUser(username)
         elif isinstance(dev, Interfaces.ITemperatureSensor):
            temp, temp_time = dev.GetTemperature()
            if temp is not None:
               for listener in self.IterDevicesImplementing(Interfaces.IThermoListener):
                  listener.ThermoUpdate(dev.SensorName(), temp)
         elif hasattr(dev, 'Step'):
            dev.Step()

   def _NewUsersFromAuthDevice(self, dev):
      """
      Returns a list of any new users authorized on dev since last check.

      A cache of the last call to dev.AuthorizedUsers() is maintained in
      Kegbot._authed_users
      """
      if not self._authed_users.has_key(dev):
         self._authed_users[dev] = []
      old = self._authed_users[dev]
      new = list(dev.AuthorizedUsers())
      ret = [x for x in new if x not in old]
      self._authed_users[dev] = new
      return ret

   def IterDevicesImplementing(self, interface):
      """ Return all registered devices that implement `interface` """
      return itertools.ifilter(lambda o: isinstance(o, interface), self._devices)

   def MainEventLoop(self):
      """ Main asynchronous service loop of the kegbot """

      self.active_flows = []
      while not self._do_quit:
         # first, give all channels a timeslice. in this timeslice, the channel
         # could notice a new flow, or service an existing flow.
         for c in self._channels:
            c.Service()

         # collect the lists of flows that require attention this time around
         all_flows = [c.active_flow for c in self._channels if c.IsActive()]
         new_flows = [f for f in all_flows if f not in self.active_flows]
         old_flows = [f for f in self.active_flows if f not in all_flows]
         self.active_flows = all_flows

         # do new-flow-specific work
         for flow in new_flows:
            self.StartFlow(flow)

         # do existing-flow-specific work -- possibly ending flows
         for flow in all_flows:
            self.StepFlow(flow)

         # do dead-flow-specific work
         for flow in old_flows:
            self.FinishFlow(flow)
            #self.active_flows.remove(flow)

         # process other things needing attention
         self._ProcessDevices()

         # sleep a bit longer if there is no guarantee of work to do next cycle
         if len(self.active_flows):
            time.sleep(0.01)
         else:
            time.sleep(0.1)

   def AuthUser(self, username):
      """
      Add user matching username to the list of authorized users.

      Returns:
         True - user added to authed_users
         False - no match for username
      """
      self.logger.info('authorizing %s' % username)
      matches = models.User.objects.filter(username=username)
      if not matches.count():
         return False

      u = matches[0]

      # TODO: for now, authorization means start a flow on all channels. we
      # may need to change this depending on (a) hardware (ie valves or no
      # valves), (b) user preference, (c) auth/key type (different behavior
      # for admin?)
      for channel in self._channels:
         channel.EnqueueUser(u)
      return True

   def UserIsAuthed(self, user):
      """ Return True if user is presently in the authed_users list """
      # guests are always authorized
      if user.get_profile().HasLabel('__default_user__'):
         return True
      for dev in self.IterDevicesImplementing(Interfaces.IAuthDevice):
         if user.username in dev.AuthorizedUsers():
            return True
      return False

   def CheckAccess(self, flow):
      """ Given a flow, return True if it should continue """
      if self._do_quit:
         self.logger.info('flow: boot: quit flag set')
         return False

      # this shouldn't happen
      if flow.channel.Keg() is None:
         self.logger.error('flow: no keg currently active; what are you trying to pour?')
         for ui in self.IterDevicesImplementing(Interfaces.IDisplayDevice):
            ui.Alert('no active keg')
         flow.channel.DeactivateFlow()
         return False

      # user is no longer authed
      if not self.UserIsAuthed(flow.user):
         self.logger.info('flow: boot: user no longer authorized')
         flow.channel.DeactivateFlow()
         return False

      # user is idle
      if flow.IdleSeconds() >= kb_common.FLOW_IDLE_TIMEOUT:
         self.logger.info('flow: boot: user went idle')
         return False

      # user has poured his maximum - DEPRECATED

      return True

   def StartFlow(self, flow):
      """ Begin a flow, based on flow passed in """
      self.logger.info('flow: starting flow handling')
      for ui in self.IterDevicesImplementing(Interfaces.IDisplayDevice):
         ui.Activity()
      channel = flow.channel

      # check if flow is permitted
      if not self.CheckAccess(flow):
         return False

      # turn on dev
      for dev in self.IterDevicesImplementing(Interfaces.IFlowListener):
         print 'flow start: %s' % dev
         dev.FlowStart(flow)

      # turn on flow
      channel.StartFlow()
      self.logger.info('flow: starting flow for user %s' % flow.user.username)

      # mark the flow as active
      self.active_flows.append(flow)
      self.logger.info('flow: new flow started for user %s on channel %s' %
            (flow.user.username, channel.chanid))

      return True

   def StepFlow(self, flow):
      """ Do periodic work on a Flow (update ui, collect volume, etc) """
      if not self.CheckAccess(flow):
         self.logger.info('flow: Flow ending in StepFlow due to CheckAccess')
         flow.channel.DeactivateFlow()
         return False

      # update things if anything changed
      for dev in self.IterDevicesImplementing(Interfaces.IFlowListener):
         dev.FlowUpdate(flow)

      return True

   def FinishFlow(self, flow):
      """Stop the flow and add to flow workqueue"""
      self.logger.info('flow: "%s" is gone; flow ending' % flow.user.username)
      flow.channel.StopFlow()
      self._flow_thread.QueueFlow(flow)
