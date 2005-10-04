#!/usr/bin/python

# keg control system
# by mike wakerly; mike@wakerly.com

# edit this line to point to your config file; that's all you have to do!
config = 'keg.cfg'

# standard lib imports
import ConfigParser
import logging
import MySQLdb
import optparse
import select
import signal
import sys
import thread
import threading
import time
import traceback
import Queue

# kegbot lib imports
import FlowController
import KegRemoteServer
import KegUI
import onewirenet
import SoundServer
import SQLConfigParser
import SQLHandler
import SQLStores as backend
import TempMonitor
import usbkeyboard
import util

# command line parser are defined here
parser = optparse.OptionParser()
parser.add_option('-D','--daemon',dest='daemon',action='store_true',help='run kegbot in daemon mode')
parser.set_defaults(daemon=False)
flags, args = parser.parse_args()

# ---------------------------------------------------------------------------- #
# Main classes
# ---------------------------------------------------------------------------- #

class KegBot:
   """ the thinking kegerator! """
   def __init__(self):
      self.QUIT          = threading.Event() # event to set when we want everything to quit
      self.config        = SQLConfigParser.SQLConfigParser()
      self.drinker_queue = Queue.Queue()
      self.ibs           = [] # list of non-hidden ibuttons
      self._allibs       = [] # like the above, but including hidden ibuttons
      self.ibs_seen      = {} # store time when IB was last seen
      self.timed_out     = [] # tokens that are connected but being ignored

      # ready to perform second stage of initialization
      self._setup()
      self._setsigs()

      # start everything up
      self.mainEventLoop()

   def _setup(self):

      # read the config
      dbcfg = ConfigParser.ConfigParser()
      dbcfg.read(config)

      # load the db info, because we will use it often enough
      self.dbhost     = dbcfg.get('DB','host')
      self.dbuser     = dbcfg.get('DB','user')
      self.dbdb       = dbcfg.get('DB','db')
      self.dbpassword = dbcfg.get('DB','password')

      self.config.read(MySQLdb.connect(host=self.dbhost,user=self.dbuser,passwd=self.dbpassword,db=self.dbdb), dbcfg.get('DB','config_table'))

      # set up logging, using the python 2.3 logging module
      self.main_logger = self.makeLogger('main',logging.INFO)

      # set up the drink, user, and key stores. these classes provide read,
      # write, and search access to information that the keg needs to know
      # about.

      # rather than retyping this stuff on each init line, just add this tuple
      # and the table name to form the init tuple
      db_tuple = (self.dbhost,self.dbuser,self.dbpassword,self.dbdb)

      self.drink_store   = backend.DrinkStore(  self, db_tuple, 'drinks' )
      self.user_store    = backend.UserStore(   self, db_tuple, 'users' )
      self.key_store     = backend.KeyStore(    self, db_tuple, 'tokens' )
      self.policy_store  = backend.PolicyStore( self, db_tuple, 'policies' )
      self.grant_store   = backend.GrantStore(  self, db_tuple, 'grants' , self.policy_store)
      self.keg_store     = backend.KegStore(    self, db_tuple, 'kegs' )
      self.thermo_store  = backend.ThermoStore( self, db_tuple, 'thermolog' )

      # set up the import stuff: the ibutton onewire network, and the LCD UI
      dev = self.config.get('devices','onewire')
      try:
         self.ownet = onewirenet.onewirenet(dev)
         self.info('main','new onewire net at device %s' % dev)
      except:
         self.ownet = None
         self.error('main','not connected to onewirenet')

      # start the sound server
      if self.config.getboolean('sounds','use_sounds'):
         self.sounds = SoundServer.SoundServer(self,self.config.get('sounds','sound_dir'))
         self.sounds.start()

      # start the remote server
      #self.server = KegRemoteServer.KegRemoteServer(self,'',9966)
      #self.server.start()

      # load the LCD-UI stuff
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

         self.keypad_fp = open(self.config.get('ui','keypad_pipe'))
         thread.start_new_thread(self.keypadThread,())
      else:
         self.lcd = Display('/dev/null')
         self.ui = KegUI.KegUI(self.lcd, self)

      # init flow meter
      dev = self.config.get('devices','flow')
      self.info('main','new flow controller at device %s' % dev)
      tickmetric = self.config.getint('flow','tick_metric')
      tick_skew = self.config.getfloat('flow','tick_skew')
      fclogger = self.makeLogger('flow', logging.INFO)
      self.fc = FlowController.FlowController(dev,ticks_per_liter = tickmetric,tick_skew = tick_skew,logger = fclogger)
      self.last_fridge_time = 0 # time since fridge event (relay trigger)

      # set up the default 'screen'. for now, it is just a boring standard
      self.ui.setCurrentPlate(self.ui.plate_main)
      self.ui.start()
      self.ui.activity()

      # start the refresh loop, which will keep self.ibs populated with the current onewirenetwork.
      if self.ownet is not None:
         thread.start_new_thread(self.ibRefreshLoop,())

      # start the flow controller status monitor
      thread.start_new_thread(self.fcStatusLoop,())

      # start the temperature monitor
      if self.config.getboolean('thermo','use_thermo'):
         self.tempsensor = TempMonitor.TempSensor(self.config.get('devices','thermo'))
         self.tempmon = TempMonitor.TempMonitor(self,self.tempsensor,self.QUIT)
         self.tempmon.start()

   def _setsigs(self):
      signal.signal(signal.SIGHUP, self.handler)
      signal.signal(signal.SIGINT, self.handler)
      signal.signal(signal.SIGQUIT,self.handler)
      signal.signal(signal.SIGTERM, self.handler)

   def handler(self,signum,frame):
      self.quit()

   def quit(self):
      self.info('main','attempting to quit')

      # hacks for blocking threads..
      #self.server.stop()
      self.fc.getStatus()
      if self.config.getboolean('sounds','use_sounds'):
         self.sounds.quit()

      # other quitting
      self.ui.stop()
      self.QUIT.set()

   def makeLogger(self,compname,level=logging.INFO):
      """ set up a logging logger, given the component name """
      ret = logging.getLogger(compname)
      ret.setLevel(level)

      # add sql handler
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

      # refuse to enable the fridge if we just disabled it. (we don't do this
      # in the disableFreezer routine, because we should always be allowed to
      # disable it.)
      min_diff = self.config.getint('timing','freezer_event_min')
      diff = time.time() - self.last_fridge_time

      if self.fc.UNKNOWN or not self.fc.fridgeStatus():
         if diff < min_diff:
            self.warning('tempmon','fridge event requested less than %i seconds after last, ignored (%i)' % (min_diff,diff))
            return
         self.last_fridge_time = time.time()
         self.fc.UNKNOWN = False
         self.info('tempmon','activated freezer curr=%s max=%s'%(curr[0],max_t))
         self.ui.plate_main.setFreezer('on ')
         self.fc.enableFridge()

   def disableFreezer(self):
      curr = self.tempmon.sensor.getTemp(1)
      min_t = self.config.getfloat('thermo','temp_max_low')

      # note: no check here for recent fridge event, because we will always
      # allow the fridge to be disabled.
      self.last_fridge_time = time.time()

      if self.fc.UNKNOWN or self.fc.fridgeStatus():
         self.fc.UNKNOWN = False
         self.info('tempmon','disabled freezer curr=%s min=%s'%(curr[0],min_t))
         self.ui.plate_main.setFreezer('off')
         self.fc.disableFridge()

   def fcStatusLoop(self):
      self.info('fc','status loop starting')
      self.last_pkt_time = 0
      timeout = self.config.getfloat('timing','fc_status_timeout')
      self.fc.getStatus()
      while not self.QUIT.isSet():
         (rr,wr,xr) = select.select([self.fc._devpipe],[],[],0.0)
         if len(rr):
            try:
               p = self.fc.recvPacket()
               self.info('fc',"read status packet " + str(p))
            except:
               self.warning('fc','packet read error')
         time.sleep(timeout)
      self.info('fc','status loop exiting')


   def keypadThread(self):
      """
      read commands from the USB keypad and send them off to our UI
      """
      self.info('keypad','keypad thread starting')
      #while not self.QUIT.isSet():
      #   e = self.ui.cmd_queue.get()

      while not self.QUIT.isSet():
         time.sleep(0.01)
         try:
            e = usbkeyboard.read_event(self.keypad_fp)
            #self.info('keypad','got event: %s' % (str(e)))
            if e[3] == 1:
               # the lcdui object may transform this key based on any
               # translation dictionary it has, eg, "KP5 = 'up', KP2 = 'down'"
               self.ui.cmd_queue.put(('usb',self.ui.translateKey(e[2])))
         except:
            pass

   def ibRefreshLoop(self):
      """
      Periodically update self.ibs with the current ibutton list.

      Because there are at least two threads (temperature monitor, main event
      loop) that require fresh status of the onewirenetwork, it is useful to
      simply refresh them constantly.

      Note that the config file may specify IB IDs to ignore (such as the
      serial controller ID or other persistent IBs). These IDs will be sored in
      _allibs but not self.ibs, and that is the only difference.
      """
      timeout = self.config.getfloat('timing','ib_refresh_timeout')

      while not self.QUIT.isSet():
         self._allibs = self.ownet.refresh()
         self.ibs = [ib for ib in self._allibs] # XXX deal with ibs to ignore
         now = time.time()
         for ib in self.ibs:
            self.ibs_seen[ib.read_id()] = now
         time.sleep(timeout)

      self.info('ibRefreshLoop','quit!')

   def lastSeen(self,ibname):
      if self.ibs_seen.has_key(ibname):
         return self.ibs_seen[ibname]
      else:
         return 0

   def mainEventLoop(self):
      while not self.QUIT.isSet():
         time.sleep(0.1)

         # update the list of idle tokens, removing ones that have left
         cutoff = time.time() - self.config.getint('timing','ib_idle_min_disconnected')
         self.timed_out = [x for x in self.timed_out if self.lastSeen(x) > cutoff]

         # check for a new ibutton, add it to the drinker queue if so
         for ib in self.ibs:
            if self.key_store.knownKey(ib.read_id()) and ib.read_id() not in self.timed_out:
               self.info('flow','found an authorized ibutton: %s' % ib.read_id())
               current_key = self.key_store.getKey(ib.read_id())
               self.drinker_queue.put_nowait(current_key.ownerid)
               break

         # look for a user to handle
         try:
            username = self.drinker_queue.get_nowait()
         except Queue.Empty:
            continue

         self.info('flow','api call to start user for %s' % username)
         uid = self.user_store.getUid(username)
         user = self.user_store.getUser(uid)

         # jump into the flow
         try:
            self.handleFlow(user)
         except:
            self.error('flow','*** UNEXPECTED ERROR - please report this bug! ***')
            traceback.print_exc()

   def handleDrinker(self,username):
      self.drinker_queue.put_nowait(username)
      return 1

   def stopFlow(self):
      self.STOP_FLOW = 1
      self.ui.plate_main.gotoPlate('last')
      return 1

   def getMaxOunces(self, grants):
      tot = 0
      for g in grants:
         oz = g.availableOunces()
         if oz == -1:
            return -1
         elif oz == 0:
            continue
         else:
            tot += oz
      return tot

   def handleFlow(self,current_user):
      self.info('flow','starting flow handling')
      self.ui.activity()
      self.STOP_FLOW = 0

      current_keg = self.keg_store.getCurrentKeg()
      if not current_keg:
         self.error('flow','no keg currently active; what are you trying to pour?')
         return

      if not current_user:
         self.error('flow','no valid user for this key; how did we get here?')
         return

      grants = self.grant_store.getGrants(current_user)
      ordered = self.grant_store.orderGrants(grants)

      # determine how many ounces [zero, inf) the user is allowed to pour
      # before we cut him off
      max_ounces = self.getMaxOunces(ordered)
      if max_ounces == 0:
         self.info('flow', 'user does not have any credit')
         self.timeoutToken(current_user)
         return
      elif max_ounces == -1:
         self.info('flow', 'user approved for unlimited ounces')
      else:
         self.info('flow', 'user approved for %.1f ounces' % max_ounces)

      # TODO: move grants to a post-processing step
      current_grant = None
      while 1:
         try:
            test = ordered.pop(0)
            if not test.isExpired(0):
               current_grant = test
               break
         except IndexError:
            self.info('flow','no valid grants found; not starting flow')
            self.timeoutToken(current_user)
            return

      self.info('flow',"current grant: %s" % (current_grant.policy.descr))

      # sequence of steps that should take place:

      # - record flow counter
      start_ticks_flow = self.fc.readTicks()
      start_ticks_grant = start_ticks_flow
      self.info('flow','current flow ticks: %s' % start_ticks_flow)

      # - turn on UI
      self.ui.plate_pour.setDrinker(current_user.getName())
      self.ui.setCurrentPlate(self.ui.plate_pour,replace=1)

      # - turn on flow
      self.fc.openValve()

      # - wait for ibutton release OR inaction timeout
      self.info('flow','starting flow for user %s' % current_user.getName())
      STOP_FLOW = 0

      idle_timeout = self.config.getfloat('timing','ib_idle_timeout')
      ceiling = self.config.getfloat('timing','ib_missing_ceiling')

      # set up the record for logging
      rec = backend.DrinkRecord(self.drink_store,current_user.id,current_keg)

      #
      # flow maintenance loop
      #
      last_flow_time = time.time()
      flow_ticks,grant_ticks = 0,0
      lastticks = 0
      old_grant = None
      idle_time = 0

      while 1:
         # if we've expired the grant, log it
         if current_grant.isExpired(current_keg.getDrinkOunces(grant_ticks)):
            rec.addFragment(current_grant,grant_ticks)
            grant_ticks = 0
            try:
               current_grant = ordered.pop(0)
               while current_grant.isExpired():
                  current_grant = ordered.pop(0)
               start_ticks_grant = self.fc.readTicks()
            except:
               current_grant = None

         if time.time() - self.last_pkt_time >= 0.5:
            self.fc.getStatus()
            self.last_pkt_time = time.time()

         # if no more grants, no more beer
         if not current_grant:
            self.info('flow','no more valid grants; ending flow')
            self.timeoutToken(current_user)
            STOP_FLOW = 1
         else:
            old_grant = current_grant

         # if the token has been gone awhile, end
         time_since_seen = time.time() - self.lastSeen(current_user)
         #if time_since_seen > ceiling:
         #   self.info('flow','ib went missing, ending flow (%s,%s)'%(time_since_seen,ceiling))
         #   STOP_FLOW = 0

         if idle_time >= idle_timeout:
            self.timeoutToken(current_user)
            STOP_FLOW = 1

         # check other credentials necessary to keep the beer flowing!
         if self.QUIT.isSet():
            STOP_FLOW = 1
         if self.STOP_FLOW:
            self.STOP_FLOW = 0
            STOP_FLOW = 1

         elif current_user in self.timed_out:
            STOP_FLOW = 1

         if STOP_FLOW:
            break

         if time.time() - last_flow_time > self.config.getfloat("flow","polltime"):

            # tick-incrementing block
            nowticks    = self.fc.readTicks()
            flow_ticks  = nowticks - start_ticks_flow
            grant_ticks = nowticks - start_ticks_grant
            ounces = round(self.fc.ticksToOunces(flow_ticks),1)
            oz = "%s oz    " % ounces

            self.ui.plate_pour.write_dict['progbar'].setProgress(self.fc.ticksToOunces(flow_ticks)/8.0)
            self.ui.plate_pour.write_dict['ounces'].setData(oz[:6])

            # record how long we have been idle in idle_time
            if lastticks == nowticks:
               idle_time += time.time() - last_flow_time
            else:
               idle_time = 0

            last_flow_time = time.time()
            lastticks = nowticks

      # at this point, the flow maintenance loop has exited. this means
      # we must quickly disable the beer flow and kick the user off the
      # system

      # - turn off flow
      self.info('flow','user is gone; flow ending')
      self.fc.closeValve()
      self.ui.setCurrentPlate(self.ui.plate_main,replace=1)

      # - record flow totals; save to user database
      # tick-incrementing block
      nowticks    = self.fc.readTicks()
      flow_ticks  = nowticks - start_ticks_flow
      grant_ticks = nowticks - start_ticks_grant

      if old_grant: # XXX - sometimes, it is None. why?
         rec.addFragment(old_grant,grant_ticks)
      else:
         self.error('flow','BUG: no old_grant, yet we\'re in the flow loop?')

      # add the final total to the record
      old_drink = self.drink_store.getLastDrink(current_user.id)
      bac = util.instantBAC(current_user,current_keg,flow_ticks)
      bac += util.decomposeBAC(old_drink[0],time.time()-old_drink[1])
      rec.emit(flow_ticks,current_grant,grant_ticks,bac)

      ounces = round(self.fc.ticksToOunces(flow_ticks),1)
      self.ui.plate_main.setLastDrink(current_user.getName(),ounces)
      self.info('flow','drink total: %i ticks, %.2f ounces' % (flow_ticks, ounces))

      # - back to idle UI

   def timeoutToken(self,id):
      self.info('timeout','timing out id %s' % id)
      self.timed_out.append(id)

   def getUser(self,ib):
      key = self.key_store.getKey(ib.read_id())
      if key:
         return self.user_store.getUser(key.getOwner())
      return None

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

   # DB Helper functions (for use with CMD line)
   # TODO: eventually we will have a suite of "public" functons that are called
   # by the external API (ie an XML-RPC delegate)
   def addUser(self,username,name = None, init_ib = None, admin = 0, email = None,aim = None):
      uid = self.user_store.addUser(username,email,aim)
      self.key_store.addKey(uid,str(init_ib))


# start a new kegbot instance, if we are called from the command line
if __name__ == '__main__':
   if flags.daemon:
      util.daemonize()
   else:
      print "Running in foreground"
   KegBot()

