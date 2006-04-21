#!/usr/bin/python2.4

# keg control system
# by mike wakerly; mike@wakerly.com

# edit this line to point to your config file; that's all you have to do!
config = 'keg.cfg'

# standard lib imports
import ConfigParser
import logging
import optparse
import signal
import socket
import sys
import threading
import time

# path hooks for local modules
sys.path.append('../pymtxorb')
sys.path.append('../pylcdui')

# kegbot lib imports
import Backend
import Flow
import Interfaces
import KegRemoteServer
import KegUI
import Publisher
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
      self.authed_users  = [] # users currently connected (usually 0 or 1)

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

      # remote event publisher
      self.publisher = Publisher.Publisher()

      # do local hardware config
      self._channels = []
      self._devices = []
      localconfig.configure(self, self.config)

      # optional module: LCD UI
      if self.config.getboolean('ui','use_lcd'):
         lcdtype = self.config.get('ui', 'lcd_type')
         dev = self.config.get('devices','lcd')
         if lcdtype == 'mtxorb':
            import mtxorb as lcddriver
            self.lcd = lcddriver.Display(dev, model=self.config.get('ui', 'lcd_model'))
         elif lcdtype == 'cfz':
            import pycfz as lcddriver
            self.lcd = lcddriver.Display(dev)
         else:
            self.logger.error('main: unknown lcd_type!')
         self.logger.info('main: new %s LCD at device %s' % (lcdtype, dev))
         self.ui = KegUI.KegUI(self.lcd, self)
         drinks = list(Backend.Drink.select(orderBy="-id", limit=1))
         if len(drinks):
            self.ui.setLastDrink(drinks[0])
      else:
         # This works fine, as long as we're cool with shared memory access to
         # the ui (and we are cool with it, for now :)
         self.ui = util.NoOpObject()

      # set up the default screen
      self.ui.setMain()
      self.ui.activity()
      self.ui.start()

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
      self.ui.stop()
      self.QUIT.set()

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
         if isinstance(dev, Interfaces.IAuthPresence):
            new_user = dev.PresenceCheck()
            if new_user:
               self.AuthUser(new_user)
            old_user = dev.AbsenceCheck()
            if old_user:
               self.DeauthUser(old_user)
         elif isinstance(dev, Interfaces.ITemperatureSensor):
            temp, temp_time = dev.GetTemperature()
            if temp is not None:
               self.publisher.PublishTemperature(dev.SensorName(), temp)
         else:
            dev.Step()

   def MainEventLoop(self):
      """ Main asynchronous service loop of the kegbot. """

      self.active_flows = []
      while not self.QUIT.isSet():
         # start any newly-created flows
         for channel in [chan for chan in self._channels if chan.IsIdle()]:
            new_flow = channel.CheckForNewFlows()
            if new_flow is not None:
               self.StartFlow(new_flow)

         # step each flow and check if it is complete
         for flow in self.active_flows:
            flow_active = self.StepFlow(flow)
            if not flow_active:
               self.FinishFlow(flow)
               self.active_flows.remove(flow)
               flow.channel.DeactivateFlow()

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
      self.authed_users.append(u)

      # TODO: for now, authorization means start a flow on all channels. we
      # may need to change this depending on (a) hardware (ie valves or no
      # valves), (b) user preference, (c) auth/key type (different behavior
      # for admin?)
      for channel in self._channels:
         channel.EnqueueUser(u)
      return True

   def DeauthUser(self, username):
      """
      Remove user matching username from the list of authorized users.

      Returns:
         True - user removed from authed_users
         False - no match for username in authed_users
      """
      matches = Backend.User.selectBy(username=username)
      if not matches.count():
         return False
      u = matches[0]
      self.authed_users = [x for x in self.authed_users if x.username != u.username]
      return True

   def UserIsAuthed(self, user):
      """ Return True if user is presently in the authed_users list """
      return user in self.authed_users

   def StopFlow(self):
      """ Cause any running flow to terminate """
      self.STOP_FLOW = 1
      self.ui.flowEnded()
      return True

   def _TotalPendingVolume(self, user):
      """
      Return the sum of all volume on all channels where this user is active.
      """
      vol = 0
      for channel in self._channels:
         if channel.flow is not None and channel.flow.user == user:
            vol += units.ticks_to_volunits(channel.flow.Ticks())
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
      if flow.IdleSeconds() >= self.config.getfloat('timing','ib_idle_timeout'):
         self.logger.info('flow: boot: user went idle')
         self.DeauthUser(flow.user.username)
         return False

      # global flow stop is set (XXX: this is a silly hack for xml-rpc)
      if self.STOP_FLOW:
         self.logger.info('flow: boot: global kill set')
         self.STOP_FLOW = 0
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
      self.ui.activity()
      self.STOP_FLOW = 0 # TODO: move to flow
      channel = flow.channel

      if flow.channel.Keg() is None:
         self.logger.error('flow: no keg currently active; what are you trying to pour?')
         self.ui.Alert('no active keg')
         self.DeauthUser(flow.user.username)
         channel.DeactivateFlow()
         return False

      if flow.max_volume <= 0:
         self.ui.Alert('no credit')
         self.DeauthUser(flow.user.username)
         channel.DeactivateFlow()
         return False

      # turn on UI
      self.ui.pourStart(flow.user.username)

      # turn on flow
      channel.StartFlow()
      self.logger.info('flow: starting flow for user %s' % flow.user.username)

      # mark the flow as active
      self.active_flows.append(flow)
      self.logger.info('flow: new flow started for user %s on channel %s' %
            (flow.user.username, channel.chanid))
      self.publisher.PublishFlowStart(flow)

      return True

   def StepFlow(self, flow):
      """ Do periodic work on a Flow (update ui, collect volume, etc) """
      if not self.CheckAccess(flow):
         self.logger.info('flow: Flow ending')
         return False

      # update things if anything changed
      channel = flow.channel
      if channel.ServiceFlow():
         curr_vol = units.ticks_to_volunits(flow.Ticks())
         curr_cost = self.EstimateCost(flow.user, curr_vol)
         self.ui.pourUpdate(units.to_ounces(curr_vol), curr_cost)

      return True

   def FinishFlow(self, flow):
      """ End a Flow and record a drink """
      self.logger.info('flow: user is gone; flow ending')
      channel = flow.channel

      # tell the channel to clean things up
      channel.StopFlow()

      # log the drink
      volume = units.ticks_to_volunits(flow.Ticks())
      d = Backend.Drink(ticks=flow.Ticks(), volume=int(volume), starttime=int(flow.start),
            endtime=int(flow.end), user=flow.user, keg=flow.channel.Keg(), status='valid')
      d.syncUpdate()

      # post-processing steps
      self.GenGrantCharges(d)
      Backend.BAC.ProcessDrink(d)
      Backend.Binge.Assign(d)
      self.publisher.PublishDrinkEvent(d)

      # update the UI
      ounces = round(units.to_ounces(volume), 2)
      self.ui.pourEnd(d)
      self.logger.info('flow: drink total: %i ticks, %i volunits, %.2f ounces' %
            (flow.Ticks(), volume, ounces))

      # de-auth the user. this may need to be configurable down the line..
      self.DeauthUser(flow.user.username)

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
      grants = self.SortByValue(list(Backend.Grant.selectBy(user=user)))
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
      grants = self.SortByValue(list(Backend.Grant.selectBy(user=d.user)))
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

