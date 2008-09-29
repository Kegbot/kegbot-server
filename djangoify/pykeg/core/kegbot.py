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

class ConfigurationError(Exception):
  """Raised when the system is misconfigured"""

# ---------------------------------------------------------------------------- #
# Main classes
# ---------------------------------------------------------------------------- #

class KegBot:
  """ the thinking kegerator! """
  def __init__(self, daemon):
    self.config = SQLConfigParser.DjangoConfigParser()
    self._is_daemon = daemon
    self._channels = {}
    self._flows = {}
    self._devices = set()
    self._threads = set()
    self._authed_users = {}
    self._do_quit = False
    self._default_user = None
    self._kb_event_queue = Queue.Queue()

    self._event_handlers = {
        kb_common.KB_EVENT.CHANNEL_ACTIVITY: self._HandleChannelActivity,
    }

    # ready to perform second stage of initialization
    self._setup()
    self._setsigs()

  def _setup(self):
    # initialize the config, from stored values in MySQL
    self.config.read(models.Config)

    # set up logging, using the python 2.3 logging module
    self._SetupLogging()

    self._logger = logging.getLogger('pykeg')

    self._logger.info('Kegbot started.')

    self._default_user = self._GetDefaultUser()

    # check schema freshness
    installed_schema = self.config.getint('db', 'schema_version')
    if installed_schema < models.SCHEMA_VERSION:
      self._logger.fatal('Error: outdated schema detected! (latest = %i, installed = %i)' %
            (installed_schema, models.SCHEMA_VERSION))
      self._logger.fatal('Please run scripts/updatedb.py to correct this.')
      self._logger.fatal('Aborting.')
      raise ConfigurationError, "Oudated schema"

    # json server
    json_server = KegbotJsonServer.KegbotJsonServer(
        ('', kb_common.JSON_SERVER_PORT_DEFAULT))
    self.AddDevice(json_server)
    self.AddThread(json_server)

    self._flow_thread = kb_threads.FlowProcessingThread(self)
    self.AddThread(self._flow_thread)

    # local hardware
    net_kegboard = Net.KegBoard()
    self.AddThread(net_kegboard)

    self._channel_0 = Flow.Channel(channel_id="0",
                                   event_queue=self._kb_event_queue,
                                   valve_relay=NoOp.Relay(),
                                   flow_meter=net_kegboard)
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
    self._logger.info('main: attempting to quit')
    self._do_quit = True

    self._logger.info('Stopping all service threads')
    for thr in self._threads:
      self._logger.info('stopping thread "%s"' % thr.getName())
      thr.Quit()
      if thr.isAlive():
        thr.join(2.0)
    self._logger.info('All service threads stopped.')
    self._logger.info('Kegbot stopped.')

    if self._logging_file_handler:
      logging.root.removeHandler(self._logging_file_handler)
    if self._logging_stdout_handler:
      logging.root.removeHandler(self._logging_stdout_handler)

  def AddChannel(self, chan):
    assert chan.channel_id() not in self._channels
    self._channels[chan.channel_id()] = chan

  def AddDevice(self, dev):
    self._devices.add(dev)

  def AddThread(self, thr):
    self._threads.add(thr)

  def _SetupLogging(self, level=logging.INFO):
    logging.root.setLevel(level)

    if not self.config.has_section('logging'):
      raise ConfigurationError, "Logging configuration not found in db"

    # add a file-output handler
    self._logging_file_handler = None
    if self.config.getboolean('logging','use_logfile'):
      self._logging_file_handler = logging.FileHandler(self.config.get('logging','logfile'))
      formatter = logging.Formatter(self.config.get('logging','logformat'))
      self._logging_file_handler.setFormatter(formatter)
      logging.root.addHandler(self._logging_file_handler)

    # add tty handler
    self._logging_stdout_handler = None
    if not self._is_daemon:
      self._logging_stdout_handler = logging.StreamHandler(sys.stdout)
      formatter = logging.Formatter(self.config.get('logging','logformat'))
      self._logging_stdout_handler.setFormatter(formatter)
      logging.root.addHandler(self._logging_stdout_handler)

  def _GetDefaultUser(self):
    """Return a |User| instance to use for unknown pours."""
    DEFAULT_USER_LABELNAME = '__default_user__'

    label_q = models.UserLabel.objects.filter(labelname=DEFAULT_USER_LABELNAME)
    if not len(label_q):
      raise ConfigurationError, ('Default user label "%s" not found.' % DEFAULT_USER_LABELNAME)

    user_q = label_q[0].userprofile_set.all()
    if not len(user_q):
      raise ConfigurationError, ('No users found with label "%s"; need at least one.' % DEFAULT_USER_LABELNAME)

    default_user = user_q[0].user
    self._logger.info('Default user for unknown flows: %s' % str(default_user))
    return default_user

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
    """Return a set of new users on |dev| since last check.

    A cache of the last call to dev.AuthorizedUsers() is maintained in
    Kegbot._authed_users
    """
    old = self._authed_users.get(dev, set())
    self._authed_users[dev] = set(dev.AuthorizedUsers())
    return (self._authed_users[dev] - old)

  def IterDevicesImplementing(self, interface):
    """Return all registered devices that implement |interface|"""
    return itertools.ifilter(lambda o: isinstance(o, interface), self._devices)

  def _StartThreads(self):
    self._logger.info('Starting all service threads')
    for thr in self._threads:
      self._logger.info('starting thread "%s"' % thr.getName())
      thr.start()
    self._logger.info('All threads started.')

  def start(self):
    self._StartThreads()
    self.MainEventLoop()

  def _HandleEvent(self, event_num, event_data):
    handler = self._event_handlers.get(event_num)
    if not handler:
      return
    handler(**event_data)

  def _HandleChannelActivity(self, channel_id, ticks):
    assert channel_id in self._channels
    channel = self._channels[channel_id]
    if not self._GetFlowForChannel(channel):
      self._StartFlow(channel)
    self._IncFlow(channel, ticks)

  def MainEventLoop(self):
    """ Main asynchronous service loop of the kegbot """
    while not self._do_quit:
      self._StepEventLoop()
      time.sleep(0.01)

  def _StepEventLoop(self):
    # first, give all channels a timeslice. in this timeslice, the channel
    # could notice a new flow, or service an existing flow.
    for c in self._channels.values():
       c.Service()

    event_num = event_data = None
    try:
      event_num, event_data = self._kb_event_queue.get_nowait()
    except Queue.Empty:
      pass

    if event_num is not None:
      self._HandleEvent(event_num, event_data)

    # do new-flow-specific work
    for flow in self._flows.values():
      if not flow:
        continue
      if not self.CheckAccess(flow):
        self.FinishFlow(flow)

    # process other things needing attention
    self._ProcessDevices()

  def AuthUser(self, username):
    """
    Add user matching username to the list of authorized users.

    Returns:
       True - user added to authed_users
       False - no match for username
    """
    self._logger.info('authorizing %s' % username)
    matches = models.User.objects.filter(username=username)
    if not matches.count():
      return False

    u = matches[0]

    # TODO: for now, authorization means start a flow on all channels. we
    # may need to change this depending on (a) hardware (ie valves or no
    # valves), (b) user preference, (c) auth/key type (different behavior
    # for admin?)
    for channel in self._channels.values():
      channel.EnqueueUser(u)
    return True

  def UserIsAuthed(self, user):
    """ Return True if user is presently in the authed_users list """
    # guests are always authorized
    if user == self._default_user:
      return True
    for dev in self.IterDevicesImplementing(Interfaces.IAuthDevice):
      if user.username in dev.AuthorizedUsers():
        return True
    return False

  def CheckAccess(self, flow):
    """ Given a flow, return True if it should continue """
    if self._do_quit:
      self._logger.info('flow: boot: quit flag set')
      return False

    # user is no longer authed
    if not self.UserIsAuthed(flow.user):
      self._logger.info('flow: boot: user no longer authorized')
      flow.channel.DeactivateFlow()
      return False

    # user is idle
    if flow.IdleSeconds() >= kb_common.FLOW_IDLE_TIMEOUT:
      self._logger.info('flow: boot: user went idle')
      return False

    return True

  def _GetKegForChannel(self, channel):
    channel_name = channel.channel_id()
    q = models.Keg.objects.filter(status='online', channel=channel_name)
    if len(q) == 0:
      return None
    else:
      return q[0]

  def _StartFlow(self, channel, user=None):
    """ Begin a flow, based on flow passed in """
    self._logger.info('Flow channel %s: starting' % channel.channel_id())
    assert not self._flows.get(channel.channel_id())

    if not user:
      user = self._default_user

    keg = self._GetKegForChannel(channel)
    if not keg:
      self._logger.warning('No keg configured on channel %s' % channel)

    flow = Flow.Flow(channel, user, keg)
    self._flows[channel.channel_id()] = flow

    # turn on dev
    for dev in self.IterDevicesImplementing(Interfaces.IFlowListener):
      dev.FlowStart(flow)

    # turn on flow
    if self.CheckAccess(flow):
      channel.StartFlow()

    self._logger.info('New flow started for user %s on channel %s' %
          (user, channel))

  def _GetFlowForChannel(self, channel):
    return self._flows.get(channel.channel_id())

  def _IncFlow(self, channel, ticks):
    flow = self._GetFlowForChannel(channel)
    if not flow:
      self._logger.warn('No flow to increment')
      return

    flow.IncTicks(ticks)
    for dev in self.IterDevicesImplementing(Interfaces.IFlowListener):
      dev.FlowUpdate(flow)

  def StepFlow(self, flow):
    """ Do periodic work on a Flow (update ui, collect volume, etc) """
    # update things if anything changed
    for dev in self.IterDevicesImplementing(Interfaces.IFlowListener):
      dev.FlowUpdate(flow)

    return True

  def FinishFlow(self, flow):
    """Stop the flow and add to flow workqueue"""
    self._logger.info('Flow channel %s: ending' % flow.channel.channel_id())
    channel = flow.channel
    channel.StopFlow()
    self._flows[channel.channel_id()] = None
    self._flow_thread.QueueFlow(flow)
