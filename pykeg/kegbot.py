#!/usr/bin/python2.4

# keg control system
# by mike wakerly; mike@wakerly.com

# edit this line to point to your config file; that's all you have to do!
config = 'keg.cfg'

# standard lib imports
import ConfigParser
import itertools
import logging
import optparse
import signal
import sys
import threading
import time

# kegbot lib imports
import Backend
import Interfaces
import KegRemoteServer
import SQLConfigParser
import units
import util

import localconfig

# command line parser are defined here
parser = optparse.OptionParser()
parser.add_option('-D','--daemon',dest='daemon',action='store_true',
      help='run kegbot in daemon mode')
parser.set_defaults(daemon=False)
flags, args = parser.parse_args()

# helper defines
NULL_DEVICES = ('', '/dev/null')

# ---------------------------------------------------------------------------- #
# Main classes
# ---------------------------------------------------------------------------- #

class KegBot:
   """ the thinking kegerator! """
   def __init__(self):
      self.QUIT          = threading.Event()
      self.config        = SQLConfigParser.SQLObjectConfigParser()
      self._channels = []
      self._devices = []
      self._authed_users = {}

      # ready to perform second stage of initialization
      self._setup()
      self._setsigs()

      # start everything up
      self.MainEventLoop()

   def _setup(self):

      # read the database config
      dbcfg = ConfigParser.ConfigParser()
      dbcfg.read(config)

      # load the db info, because we will use it often enough
      self.dbhost = dbcfg.get('DB','host')
      self.dbuser = dbcfg.get('DB','user')
      self.dbdb = dbcfg.get('DB','db')
      self.dbpassword = dbcfg.get('DB','password')

      # connect to db - TODO: remove mysql component and make the URI the sole
      # config option
      db_uri = 'mysql://%s:%s@%s/%s' % (self.dbuser, self.dbpassword,
            self.dbhost, self.dbdb)
      Backend.setup(db_uri)

      # initialize the config, from stored values in MySQL
      self.config.read(Backend.Config)

      # set up logging, using the python 2.3 logging module
      self._SetupLogging()
      self.logger = logging.getLogger('pykeg')

      # check schema freshness
      installed_schema = self.config.getint('db', 'schema_version')
      if installed_schema < Backend.SCHEMA_VERSION:
         self.logger.fatal('Error: outdated schema detected! (latest = %i, installed = %i)' %
               (installed_schema, Backend.SCHEMA_VERSION))
         self.logger.fatal('Please run scripts/updatedb.py to correct this.')
         self.logger.fatal('Aborting.')
         sys.exit(1)

      # remote server
      self.server = KegRemoteServer.KegRemoteServer(self, '', 9966)
      self.server.start()

      # do local hardware config
      localconfig.configure(self, self.config)

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

      # other quitting
      self.server.stop()
      self.QUIT.set()

      # XXX TODO: stop all devices that have a stop method

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
      if not flags.daemon:
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
      new = dev.AuthorizedUsers()
      ret = [x for x in new if x not in old]
      self._authed_users[dev] = new
      return ret

   def IterDevicesImplementing(self, interface):
      """ Return all registered devices that implement `interface` """
      return itertools.ifilter(lambda o: isinstance(o, interface), self._devices)

   def MainEventLoop(self):
      """ Main asynchronous service loop of the kegbot """

      self.active_flows = []
      while not self.QUIT.isSet():
         # service all channels
         for c in self._channels:
            c.Service()

         all_flows = [c.active_flow for c in self._channels if not c.IsIdle()]

         new_flows = [f for f in all_flows if f not in self.active_flows]
         old_flows = [f for f in self.active_flows if f not in all_flows]

         # do existing-flow-specific work -- possibly ending flows
         self.active_flows = all_flows
         for flow in all_flows:
            self.StepFlow(flow)

         # do new-flow-specific work
         for flow in new_flows:
            self.StartFlow(flow)

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
      matches = Backend.User.selectBy(username=username)
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
      if user.HasLabel('guest'):
         return True
      for dev in self.IterDevicesImplementing(Interfaces.IAuthDevice):
         if user.username in dev.AuthorizedUsers():
            return True
      return False

   def _TotalPendingVolume(self, user):
      """
      Return the sum of all volume on all channels where this user is active.
      """
      vol = 0
      for channel in self._channels:
         if channel.active_flow is not None and channel.active_flow.user == user:
            vol += units.ticks_to_volunits(channel.active_flow.Ticks())
      return vol

   def CheckAccess(self, flow):
      """ Given a flow, return True if it should continue """
      if self.QUIT.isSet():
         self.logger.info('flow: boot: quit flag set')
         return False

      # user is no longer authed
      if not self.UserIsAuthed(flow.user):
         self.logger.info('flow: boot: user no longer authorized')
         return False

      # user is idle
      # TODO: fix me with a new config value (ib_idle_timeout doesn't look right)
      if flow.IdleSeconds() >= 10:
         self.logger.info('flow: boot: user went idle')
         return False

      # user has poured his maximum
      if flow.max_volume != sys.maxint:
         # we have to check not just the amount poured on this flow, but any
         # amount poured simultaneously on other channels
         volume = self._TotalPendingVolume(flow.user)
         if volume >= flow.max_volume:
            self.logger.info('flow: boot: volume limit met/exceeded')
            return False

      return True

   def StartFlow(self, flow):
      """ Begin a flow, based on flow passed in """
      self.logger.info('flow: starting flow handling')
      for ui in self.IterDevicesImplementing(Interfaces.IDisplayDevice):
         ui.Activity()
      channel = flow.channel

      # XXX FIXME
      if 0 and flow.channel.Keg() is None:
         self.logger.error('flow: no keg currently active; what are you trying to pour?')
         for ui in self.IterDevicesImplementing(Interfaces.IDisplayDevice):
            ui.Alert('no active keg')
         channel.DeactivateFlow()
         return False

      if 0 and flow.max_volume <= 0:
         for ui in self.IterDevicesImplementing(Interfaces.IDisplayDevice):
            ui.Alert('no credit')
         channel.DeactivateFlow()
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
      curr_vol = units.ticks_to_volunits(flow.Ticks())
      flow.est_cost = self.EstimateCost(flow.user, curr_vol)
      for dev in self.IterDevicesImplementing(Interfaces.IFlowListener):
         dev.FlowUpdate(flow)

      return True

   def FinishFlow(self, flow):
      """ End a Flow and record a drink """
      self.logger.info('flow: user is gone; flow ending')
      channel = flow.channel

      # tell the channel to clean things up
      channel.StopFlow()

      # nothing to do if null pour
      if flow.Ticks() <= 0:
         return

      # log the drink
      volume = units.ticks_to_volunits(flow.Ticks())
      d = Backend.Drink(ticks=flow.Ticks(), volume=int(volume), starttime=flow.start,
            endtime=flow.end, user=flow.user, keg=flow.channel.Keg(), status='valid')
      d.syncUpdate()

      # post-processing steps
      self.GenGrantCharges(d)
      Backend.BAC.ProcessDrink(d)
      Backend.Binge.Assign(d)

      # update the UI
      ounces = round(units.to_ounces(volume), 2)
      for dev in self.IterDevicesImplementing(Interfaces.IFlowListener):
         dev.FlowEnd(flow, d)
      self.logger.info('flow: drink total: %i ticks, %i volunits, %.2f ounces' %
            (flow.Ticks(), volume, ounces))

   def SortByValue(self, grants):
      """ return a list of grants sorted by least cost to user """
      def valsort(a, b):
         # TODO consider value of expirations
         ret = cmp(b.policy.unitcost, a.policy.unitcost)
         return ret

      grants.sort(valsort)
      return grants

   def EstimateCost(self, user, volume):
      """ Given a user and a volume, estimate the cost of that volume. """
      # this function is somewhat wasteful; thankfully sqlobject is caching the
      # results from the select, else we'd be doing way too many
      grants = self.SortByValue(user.grants)
      vol_remain = volume
      cost = 0.0
      while vol_remain > 0:
         try:
            g = grants.pop()
         except IndexError:
            break
         vol_curr = min(g.AvailableVolume(), vol_remain)
         cost += g.policy.Cost(vol_curr)
         vol_remain -= vol_curr
      return cost

   def GenGrantCharges(self, d):
      """ Create and store one or more grant charges given a recent drink """
      grants = self.SortByValue(d.user.grants)
      vol_remain = d.volume
      while vol_remain > 0:
         try:
            g = grants.pop()
         except IndexError:
            break
         vol_curr = min(g.AvailableVolume(), vol_remain)
         if vol_curr > 0:
            c = Backend.GrantCharge(grant=g, drink=d, user=d.user, volume=vol_curr)
            c.syncUpdate()
            g.IncVolume(vol_curr)
         vol_remain -= vol_curr

      if vol_remain > 0:
         # TODO: charge to default grant
         self.logger.warning('flow: volume not charged: %i' % vol_remain)


# start a new kegbot instance, if we are called from the command line
if __name__ == '__main__':
   if sys.version_info < (2,3):
      print>>sys.stderr, 'kegbot requires Python 2.3 or later; aborting'
      sys.exit(1)
   if flags.daemon:
      print 'Running in background'
      util.daemonize()
   else:
      print 'Running in foreground'
   KegBot()

