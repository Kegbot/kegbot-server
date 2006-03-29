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
import sys
import threading
import time
import Queue

# path hooks for local modules
sys.path.append('../pymtxorb')
sys.path.append('../pylcdui')

# kegbot lib imports
import Auth
import Backend
import Flow
import FlowController
import KegRemoteServer
import KegUI
import SQLConfigParser
import TempMonitor
import units
import util

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
      self.logger = self.MakeLogger('main',logging.INFO)

      self.server = KegRemoteServer.KegRemoteServer(self, '', 9966)
      self.server.start()

      # optional module: usb ibutton auth
      if self.config.getboolean('auth','usb_ib'):
         timeout = self.config.getfloat('timing','ib_refresh_timeout')
         logger = self.MakeLogger('usb_ibauth',logging.INFO)
         usb_ibauth = Auth.USBIBAuth(self, 'usb', timeout, self.QUIT, logger)
         usb_ibauth.start()

      # optional module: serial ibutton auth
      if self.config.getboolean('auth','serial_ib'):
         dev = self.config.get('devices','onewire')
         timeout = self.config.getfloat('timing','ib_refresh_timeout')
         logger = self.MakeLogger('serial_ibauth',logging.INFO)
         serial_ibauth = Auth.SerialIBAuth(self, dev, timeout, self.QUIT, logger)
         serial_ibauth.start()

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

      # optional module: temperature monitor
      if self.config.getboolean('thermo','use_thermo'):
         self.tempsensor = TempMonitor.TempSensor(self.config.get('devices','thermo'))
         self.tempmon = TempMonitor.TempMonitor(self,self.tempsensor,self.QUIT)
         self.tempmon.start()

      # initialize flow meter
      dev = self.config.get('devices','flow')
      self.logger.info('main: new flow controller at device %s' % dev)
      if dev in NULL_DEVICES:
         self.fc = FlowController.FlowSimulator()
      else:
         self.fc = FlowController.FlowController(dev, self.MakeLogger('flow', logging.INFO))
         self.fc.start()

      # set up channels. TODO: assuming one keg (single channel) at the moment
      self.channels = [Flow.Channel(self.fc, self.MakeLogger('channel0'))]

      # set up the default screen
      self.ui.setMain()
      self.ui.activity()
      self.ui.start()

   def _setsigs(self):
      """ Sets HUP, INT, QUIT, TERM to go to cause a quit """
      signal.signal(signal.SIGHUP, self._SignalHandler)
      signal.signal(signal.SIGINT, self._SignalHandler)
      signal.signal(signal.SIGQUIT,self._SignalHandler)
      signal.signal(signal.SIGTERM, self._SignalHandler)

   def _SignalHandler(self, signum, frame):
      """ All handled signals cause a quit """
      self.Quit()

   def Quit(self):
      self.logger.info('main: attempting to quit')

      # other quitting
      self.server.stop()
      self.fc.stop()
      self.ui.stop()
      self.QUIT.set()

   def MakeLogger(self, compname, level=logging.INFO):
      """ set up a logging logger, given the component name """
      ret = logging.getLogger(compname)
      ret.setLevel(level)

      # add sql handler -- XXX TODO: deprecated, move to sqlobjet
      if self.config.getboolean('logging','use_sql'):
         try:
            hdlr = SQLHandler.SQLHandler(self.dbhost, self.dbuser,
                  self.dbdb, self.config.get('logging','logtable'),
                  self.dbpassword)
            hdlr.setLevel(logging.WARNING)
            formatter = SQLHandler.SQLVerboseFormatter()
            hdlr.setFormatter(formatter)
            ret.addHandler(hdlr)
         except:
            ret.warning("Could not start SQL Handler")

      # add a file-output handler
      if self.config.getboolean('logging','use_logfile'):
         hdlr = logging.FileHandler(self.config.get('logging','logfile'))
         formatter = logging.Formatter(self.config.get('logging','logformat'))
         hdlr.setFormatter(formatter)
         ret.addHandler(hdlr)

      # add tty handler
      if not flags.daemon:
         hdlr = logging.StreamHandler(sys.stdout)
         formatter = logging.Formatter(self.config.get('logging','logformat'))
         hdlr.setFormatter(formatter)
         ret.addHandler(hdlr)

      return ret

   def MainEventLoop(self):
      active_flows = []
      while not self.QUIT.isSet():
         for channel in self.channels:
            new_flow = channel.MaybeActivateNextFlow()
            if new_flow is not None:
               success = self.StartFlow(new_flow)
               if success:
                  self.logger.info('flow: new flow started for user %s on channel %s' %
                        (new_flow.user.username, channel))
                  active_flows.append(new_flow)
               else:
                  channel.DeactivateFlow()
                  self.logger.info('flow: flow not started')

         # step each flow and check if it is complete
         for flow in active_flows:
            flow_active = self.StepFlow(flow)
            if not flow_active:
               self.FinishFlow(flow)
               active_flows.remove(flow)
               channel.DeactivateFlow()

         # sleep a bit longer if there is no guarantee of work to do next cycle
         if len(active_flows):
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
      if matches.count():
         u = matches[0]
         self.authed_users.append(u)
         # TODO: explicit support for channels
         self.channels[0].EnqueueFlow(self.CreateFlow(u))
         return True
      return False

   def DeauthUser(self, username):
      """
      Remove user matching username from the list of authorized users.

      Returns:
         True - user removed from authed_users
         False - no match for username in authed_users
      """
      matches = Backend.User.selectBy(username=username)
      if matches.count():
         u = matches[0]
         self.authed_users = [x for x in self.authed_users if x.username != u.username]
         return True
      return False

   def UserIsAuthed(self, user):
      """ Return True if user is presently in the authed_users list """
      return user in self.authed_users

   def StopFlow(self):
      """ Cause any running flow to terminate """
      self.STOP_FLOW = 1
      self.ui.flowEnded()
      return True

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
      if flow.IdleSeconds() >= self.config.getfloat('timing','ib_idle_timeout'):
         self.logger.info('flow: boot: user went idle')
         self.timeoutUser(flow.user)
         return False

      # global flow stop is set (XXX: this is a silly hack for xml-rpc)
      if self.STOP_FLOW:
         self.logger.info('flow: boot: global kill set')
         self.STOP_FLOW = 0
         return False

      # user has poured his maximum
      if flow.max_volume != sys.maxint:
         volume = units.ticks_to_volunits(flow.Ticks())
         if volume >= flow.max_volume:
            self.logger.info('flow: boot: volume limit met/exceeded')
            return False

      return True

   def CurrentKeg(self):
      online_kegs = list(Backend.Keg.selectBy(status='online', orderBy='-id'))
      if len(online_kegs) == 0:
         return None
      else:
         return online_kegs[0]

   def CreateFlow(self, user):
      """ Create a generic Flow.Flow object for given user """
      grants = list(Backend.Grant.selectBy(user=user))

      # determine how much volume [zero, inf) the user is allowed to pour
      # before we cut him off
      max_volume = util.MaxVolume(grants)
      if max_volume == 0:
         self.logger.info('flow: user does not have any credit')
      elif max_volume == sys.maxint:
         self.logger.info('flow: user approved for unlimited volume')
      else:
         self.logger.info('flow: user approved for %.1f volunits' % max_volume)

      return Flow.Flow(self.channels[0], user = user, max_volume = max_volume)

   def StartFlow(self, flow):
      """ Begin a flow, based on flow passed in """
      self.logger.info('flow: starting flow handling')
      self.ui.activity()
      self.STOP_FLOW = 0

      current_keg = self.CurrentKeg()
      if not current_keg:
         self.logger.error('flow: no keg currently active; what are you trying to pour?')
         self.timeoutUser(flow.user)
         return False
      flow.keg = current_keg

      if flow.max_volume <= 0:
         self.ui.Alert('no credit!')
         self.timeoutUser(flow.user)
         return False

      # turn on UI
      self.ui.setDrinker(flow.user.username)
      self.ui.setCurrentPlate(self.ui.plate_pour, replace=1)

      # turn on flow
      flow.channel.fc.openValve()

      # zero the flow on current tick reading
      flow.SetTicks(flow.channel.fc.readTicks())
      self.logger.info('flow: starting flow for user %s' % flow.user.username)

      return True

   def StepFlow(self, flow):
      """ Do periodic work on a Flow (update ui, collect volume, etc) """
      if not self.CheckAccess(flow):
         self.logger.info('flow: Flow ending')
         return False

      # update things if anything changed
      if flow.SetTicks(flow.channel.fc.readTicks()):
         curr_vol = units.ticks_to_volunits(flow.Ticks())
         curr_cost = self.EstimateCost(flow.user, curr_vol)
         self.ui.pourUpdate(units.to_ounces(curr_vol), curr_cost)

      return True

   def FinishFlow(self, flow):
      """ End a Flow and record a drink """
      self.logger.info('flow: user is gone; flow ending')
      flow.channel.fc.closeValve()
      self.ui.setCurrentPlate(self.ui.plate_main, replace=1)

      # record flow totals; save to user database
      flow.SetTicks(flow.channel.fc.readTicks())
      flow.end = time.time()
      volume = units.ticks_to_volunits(flow.Ticks())

      # log the drink
      d = Backend.Drink(ticks=flow.Ticks(), volume=int(volume), starttime=int(flow.start),
            endtime=int(flow.end), user=flow.user, keg=flow.keg, status='valid')
      d.syncUpdate()

      # post-processing steps
      self.GenGrantCharges(d)
      Backend.BAC.ProcessDrink(d)
      Backend.Binge.Assign(d)

      # update the UI
      ounces = round(units.to_ounces(volume),2)
      self.ui.setLastDrink(d)
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
         if vol_curr > 0:
            cost += g.policy.Cost(vol_remain)
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

   def timeoutUser(self, user):
      """ Callback executed when a user goes idle """
      self.DeauthUser(user.username)


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

