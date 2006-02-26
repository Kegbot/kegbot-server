#!/usr/bin/python

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
import thread
import threading
import time
import traceback
import Queue

# path hooks for local modules
sys.path.append('../pymtxorb')
sys.path.append('../pylcdui')

# kegbot lib imports
import Auth
import Backend
import FlowController
import KegRemoteServer
import KegUI
import SQLConfigParser
import TempMonitor
import units
import util

# other (third-party) lib imports
import sqlobject

# command line parser are defined here
parser = optparse.OptionParser()
parser.add_option('-D','--daemon',dest='daemon',action='store_true',
      help='run kegbot in daemon mode')
parser.set_defaults(daemon=False)
flags, args = parser.parse_args()

# helper defines
NULL_DEVICES = ('', '/dev/null')
MILLILITERS_PER_OUNCE = 29.5735297

# ---------------------------------------------------------------------------- #
# Main classes
# ---------------------------------------------------------------------------- #

class KegBot:
   """ the thinking kegerator! """
   def __init__(self):
      self.QUIT          = threading.Event() # event to set when we want everything to quit
      self.config        = SQLConfigParser.SQLObjectConfigParser()
      self.drinker_queue = Queue.Queue()
      self.authed_users  = [] # users currently connected (usually 0 or 1)

      # ready to perform second stage of initialization
      self._setup()
      self._setsigs()

      # start everything up
      self.mainEventLoop()

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
      db_uri = 'mysql://%s:%s@%s/%s' % (self.dbuser, self.dbpassword, self.dbhost, self.dbdb)
      connection = sqlobject.connectionForURI(db_uri)
      sqlobject.sqlhub.processConnection = connection

      # initialize the config, from stored values in MySQL
      self.config.read(Backend.Config)

      # set up logging, using the python 2.3 logging module
      self.main_logger = self.makeLogger('main',logging.INFO)

      self.server = KegRemoteServer.KegRemoteServer(self, '', 9966)
      self.server.start()

      # optional module: serial ibutton auth
      dev = self.config.get('devices','onewire')
      if dev not in NULL_DEVICES:
         timeout = self.config.getfloat('timing','ib_refresh_timeout')
         logger = self.makeLogger('serial_ibauth',logging.INFO)
         serial_ibauth = Auth.SerialIBAuth(self, timeout, self.QUIT, logger)
         serial_ibauth.start()

      # optional module: usb ibutton auth
      if self.config.getboolean('auth','usb_ib'):
         timeout = self.config.getfloat('timing','ib_refresh_timeout')
         logger = self.makeLogger('usb_ibauth',logging.INFO)
         usb_ibauth = Auth.USBIBAuth(self, timeout, self.QUIT, logger)
         usb_ibauth.start()

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
            self.error('main', 'unknown lcd_type!')
         self.info('main','new %s LCD at device %s' % (lcdtype, dev))
         self.ui = KegUI.KegUI(self.lcd, self)

      else:
         # TODO: replace me with a KegUI.NullUI instance
         self.lcd = Display('/dev/null')
         self.ui = KegUI.KegUI(self.lcd, self)

      # optional module: temperature monitor
      if self.config.getboolean('thermo','use_thermo'):
         self.tempsensor = TempMonitor.TempSensor(self.config.get('devices','thermo'))
         self.tempmon = TempMonitor.TempMonitor(self,self.tempsensor,self.QUIT)
         self.tempmon.start()

      # initialize flow meter
      dev = self.config.get('devices','flow')
      self.info('main','new flow controller at device %s' % dev)
      if dev in NULL_DEVICES:
         self.fc = FlowController.FlowSimulator()
      else:
         self.fc = FlowController.FlowController(dev, self.makeLogger('flow', logging.INFO))
         self.fc.start()

      # set up the default screen
      self.ui.setMain()
      self.ui.activity()
      self.ui.start()

   def _setsigs(self):
      signal.signal(signal.SIGHUP, self.handler)
      signal.signal(signal.SIGINT, self.handler)
      signal.signal(signal.SIGQUIT,self.handler)
      signal.signal(signal.SIGTERM, self.handler)

   def handler(self, signum, frame):
      self.quit()

   def quit(self):
      self.info('main','attempting to quit')

      # other quitting
      self.server.stop()
      self.fc.stop()
      self.ui.stop()
      self.QUIT.set()

   def makeLogger(self,compname,level=logging.INFO):
      """ set up a logging logger, given the component name """
      ret = logging.getLogger(compname)
      ret.setLevel(level)

      # add sql handler -- XXX TODO: deprecated, move to sqlobjet
      if self.config.getboolean('logging','use_sql'):
         try:
            hdlr = SQLHandler.SQLHandler(self.dbhost,self.dbuser,self.dbdb,self.config.get('logging','logtable'),self.dbpassword)
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

   def enableFreezer(self):
      curr = self.tempmon.sensor.getTemp(1) # XXX - sensor index is hardcoded! add to .config
      max_t = self.config.getfloat('thermo','temp_max_high')

      if not self.fc.fridgeStatus():
         self.info('tempmon','activated freezer curr=%s max=%s'%(curr[0],max_t))
         self.ui.setFreezer('on ')
         self.fc.enableFridge()

   def disableFreezer(self):
      curr = self.tempmon.sensor.getTemp(1)
      min_t = self.config.getfloat('thermo','temp_max_low')

      if self.fc.fridgeStatus():
         self.info('tempmon','disabled freezer curr=%s min=%s'%(curr[0],min_t))
         self.ui.setFreezer('off')
         self.fc.disableFridge()

   def mainEventLoop(self):
      while not self.QUIT.isSet():
         time.sleep(0.1)

         # look for a user to handle
         try:
            user = self.authed_users[0]
         except IndexError:
            continue

         self.info('flow','api call to start user for %s' % user.username)
         # jump into the flow
         try:
            self.handleFlow(user)
         except:
            self.critical('flow','UNEXPECTED ERROR - please report this bug!')
            traceback.print_exc()
            sys.exit(1)

   def authUser(self, username):
      matches = Backend.User.selectBy(username=username)
      if matches.count():
         u = matches[0]
         self.authed_users.append(u)
         return True
      return False

   def deauthUser(self, username):
      matches = Backend.User.selectBy(username=username)
      if matches.count():
         u = matches[0]
         self.authed_users = [x for x in self.authed_users if x.username != u.username]
         return True
      return False

   def userIsAuthed(self, user):
      return user in self.authed_users

   def stopFlow(self):
      self.STOP_FLOW = 1
      self.ui.flowEnded()
      return 1

   def checkAccess(self, current_user, idle_time, volume, max_volume):
      if self.QUIT.isSet():
         self.info('flow', 'boot: quit flag set')
         return 0

      # user is no longer authed
      if not self.userIsAuthed(current_user):
         self.info('flow', 'boot: user no longer authorized')
         return 0

      # user is idle
      if idle_time >= self.config.getfloat('timing','ib_idle_timeout'):
         self.info('flow', 'boot: user went idle')
         self.timeoutUser(current_user)
         return 0

      # global flow stop is set (XXX: this is a silly hack for xml-rpc)
      if self.STOP_FLOW:
         self.info('flow', 'boot: global kill set')
         self.STOP_FLOW = 0
         return 0

      # user has poured his maximum
      if max_volume != sys.maxint:
         if volume >= max_volume:
            self.info('flow', 'boot: volume limit met/exceeded')
            return 0

      return 1

   def handleFlow(self, current_user):
      self.info('flow','starting flow handling')
      self.ui.activity()
      self.STOP_FLOW = 0

      online_kegs = list(Backend.Keg.selectBy(status='online', orderBy='-id'))
      if len(online_kegs) == 0:
         self.error('flow','no keg currently active; what are you trying to pour?')
         self.timeoutUser(current_user)
         return
      else:
         current_keg = online_kegs[0]

      if not current_user:
         self.error('flow','no valid user for this key; how did we get here?')
         return

      grants = list(Backend.Grant.selectBy(user=current_user))

      # determine how much volume [zero, inf) the user is allowed to pour
      # before we cut him off
      max_volume = util.MaxVolume(grants)
      if max_volume == 0:
         self.info('flow', 'user does not have any credit')
         self.timeoutUser(current_user)
         return
      elif max_volume == sys.maxint:
         self.info('flow', 'user approved for unlimited volume')
      else:
         self.info('flow', 'user approved for %.1f volunits' % max_volume)

      # turn on UI
      self.ui.setDrinker(current_user.username)
      self.ui.setCurrentPlate(self.ui.plate_pour,replace=1)

      # turn on flow
      self.fc.openValve()
      start_ticks_flow = self.fc.readTicks()
      self.info('flow','current flow ticks: %s' % start_ticks_flow)
      self.info('flow','starting flow for user %s' % current_user.username)

      #
      # flow maintenance loop
      #
      last_flow_time = time.time()  # time since last change in flow count
      start_time = time.time()      # timestamp of flow start
      flow_ticks = 0                # ticks in current flow
      lastticks = 0                 # temporary value for storing last flow reading
      curr_vol = 0.0                # volume of current flow

      while 1:
         looptime = time.time()

         # check user access
         idle_amt = looptime - last_flow_time
         if not self.checkAccess(current_user, idle_amt, curr_vol, max_volume):
            break

         # touch the last flow time if the user wasn't idle, and update ui
         # if flow happened
         nowticks = self.fc.readTicks()
         if lastticks != nowticks:
            last_flow_time = looptime
            flow_ticks = nowticks - start_ticks_flow
            curr_vol = self.ticksToVolunits(flow_ticks)
            self.ui.pourUpdate(self.volunitsToOunces(curr_vol))

         lastticks = nowticks

      # turn off flow
      looptime = time.time()
      self.info('flow','user is gone; flow ending')
      self.fc.closeValve()
      self.ui.setCurrentPlate(self.ui.plate_main, replace=1)

      # record flow totals; save to user database
      nowticks = self.fc.readTicks()
      flow_ticks = nowticks - start_ticks_flow
      volume = self.ticksToVolunits(flow_ticks)

      # log the drink
      d = Backend.Drink(ticks=flow_ticks, volume=int(volume), starttime=int(start_time),
            endtime=int(looptime), user=current_user,
            keg=current_keg, status='valid')
      d.syncUpdate()

      # post-processing steps
      self.GrantCalculate(d)
      self.BACCalculate(d)
      self.BingeUpdate(d)

      # update the UI
      ounces = round(self.volunitsToOunces(volume),2)
      #self.ui.setLastDrink(current_user.username,ounces)
      self.info('flow','drink total: %i ticks, %i volunits, %.2f ounces' % (flow_ticks, volume, ounces))

      # de-auth the user. this may need to be configurable down the line..
      self.deauthUser(current_user.username)

   def SortByValue(self, grants):
      """ return a list of grants sorted by least cost to user """
      def valsort(a, b):
         # TODO consider value of expirations
         ret = cmp(b.policy.unitcost, a.policy.unitcost)
         return ret

      grants.sort(valsort)
      return grants

   def GrantCalculate(self, d):
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
         print 'ERROR: volume not charged: %i' % vol_remain
         # XXX TODO charge to default grant

   def BingeUpdate(self, d):
      binges = list(Backend.Binge.select("user_id=%i"%d.user.id,
         orderBy="-id", limit=1))

      # flush binge fetched if it is too old
      if len(binges) != 0:
         if binges[0].endtime < (d.endtime - (60*90)): # XXX fix constant
            binges = []

      # now find or create the current binge, and update it
      if len(binges) == 0:
         last_binge = Backend.Binge(user=d.user, startdrink=d,
               enddrink=d, volume=d.volume, starttime=d.endtime,
               endtime=d.endtime)
         last_binge.syncUpdate()
      else:
         last_binge = binges[0]
         last_binge.volume += d.volume
         last_binge.enddrink = d
         last_binge.endtime = d.endtime
         last_binge.syncUpdate()

   def BACCalculate(self, d):
      curr_bac = 0.0
      matches = Backend.BAC.selectBy(user=d.user, orderBy='-rectime')
      if matches.count():
         last_bac = matches[0]
         curr_bac = util.decomposeBAC(last_bac.bac, time.time() - last_bac.rectime)
      curr_bac += util.instantBAC(d.user, d.keg, self.volunitsToOunces(d.volume))
      b = Backend.BAC(user=d.user, drink=d.id, rectime=int(time.time()), bac=curr_bac)
      d.syncUpdate()

   def timeoutUser(self, user):
      self.deauthUser(user.username)

   ### volume related helper functions
   def ticksToVolunits(self, ticks):
      return ticks

   def volunitsToOunces(self, volunits):
      return float(volunits)/units.US_OUNCE

   def volunitsToLiters(self, volunits):
      return float(volunits)/units.LITER

   ### logging related helper functions
   def log(self,component,message):
      self.main_logger.info("%s: %s" % (component,message))

   def info(self,component,message):
      self.main_logger.info("%s: %s" % (component,message))

   def warning(self,component,message):
      self.main_logger.warning("%s: %s" % (component,message))

   def error(self,component,message):
      self.main_logger.error("%s: %s" % (component,message))

   def critical(self,component,message):
      self.main_logger.critical("%s: %s" % (component,message))

# start a new kegbot instance, if we are called from the command line
if __name__ == '__main__':
   if sys.version_info < (2,3):
      print 'kegbot requires Python 2.3 or later; aborting'
      sys.exit(1)
   if flags.daemon:
      util.daemonize()
   else:
      print "Running in foreground"
   KegBot()

