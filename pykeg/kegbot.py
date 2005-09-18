#!/usr/bin/python

# keg control system
# by mike wakerly; mike@wakerly.com

import ConfigParser
import logging
import optparse
import os
import select
import signal
import thread
import threading
import time
import traceback
import Queue

import FlowController
import KegRemoteServer
import lcdui
import onewirenet
import pycfz as lcddriver
import SoundServer
import SQLConfigParser
import SQLHandler
import SQLStores as backend
import TempMonitor
import usbkeyboard

# edit this line to point to your config file; that's all you have to do!
config = 'keg.cfg'

# command line parser are defined here
parser = optparse.OptionParser()
parser.add_option('-D','--daemon',dest='daemon',action='store_true',help='run kegbot in daemon mode')
parser.set_defaults(daemon=False)
(flags, args) = parser.parse_args()

# ---------------------------------------------------------------------------- #
# Helper functions -- available to all classes
# ---------------------------------------------------------------------------- #
def daemonize():
   # Fork once
   if os.fork() != 0:
      os._exit(0)
   os.setsid()  # Create new session
   # Fork twice
   if os.fork() != 0:
      os._exit(0)
   os.chdir("/")
   os.umask(0)

   try:
      maxfd = os.sysconf("SC_OPEN_MAX")
   except (AttributeError, ValueError):
      maxfd = 256

   for fd in range(0, maxfd):
      try:
         os.close(fd)
      except OSError:
         pass

   os.open('/dev/null', os.O_RDONLY)
   os.open('/dev/null', os.O_RDWR)
   os.open('/dev/null', os.O_RDWR)

def instantBAC(user,keg,drink_ticks):
   # calculate weight in metric KGs
   if user.weight <= 0:
      return 0.0

   kg_weight = user.weight/2.2046
   ounces = keg.getDrinkOunces(drink_ticks)

   # gender based water-weight
   if user.gender == 'male':
         waterp = 0.58
   else:
      waterp = 0.49

   # find total body water (in milliliters)
   bodywater = kg_weight * waterp * 1000.0

   # weight in grams of 1 oz alcohol
   alcweight = 29.57*0.79;

   # rate of alcohol per subject's total body water
   alc_per_body_ml = alcweight/bodywater

   # find alcohol concentration in blood (80.6% water)
   alc_per_blood_ml = alc_per_body_ml * 0.806

   # switch to "grams percent"
   grams_pct = alc_per_blood_ml * 100.0

   # determine how much we've really consumed
   alc_consumed = ounces * (keg.alccontent/100.0)
   instant_bac = alc_consumed * grams_pct

   return instant_bac

def decomposeBAC(bac,seconds_ago,rate=0.02):
   return max(0.0,bac - (rate * (seconds_ago/3600.0)))

def toF(t):
   return ((9.0/5.0)*t) + 32

# ---------------------------------------------------------------------------- #
# Main classes
# ---------------------------------------------------------------------------- #

class KegBot:
   """ the thinking kegerator! """
   def __init__(self):

      # this init function is now split in to two sections, to support online
      # reloading of compiled component code.

      self.QUIT = threading.Event() # event to set when we want everything to quit
      self.setsigs() # set up handlers for control-c, kill signals

      self.config = SQLConfigParser.SQLConfigParser()
      self.ibs = []
      self._allibs = []
      self.ibs_seen = {} # store time when IB was last seen
      self.drinker_queue = Queue.Queue()

      # a list of buttons (probably just zero or one) that have been connected
      # for too long. if in this list, the mainEventLoop will wait for the
      # button to 'go away' for awhile until it will recognize it again. among
      # other things, this keeps a normally-closed solenoid valve from burning
      # out
      self.timed_out = []

      # ready to perform second stage of initialization
      self._setup()

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
         self.error('main','not connected to onewirenet')

      # start the sound server
      if self.config.getboolean('sounds','use_sounds'):
         self.sounds = SoundServer.SoundServer(self,self.config.get('sounds','sound_dir'))
         self.sounds.start()

      # start the remote server
      self.server = KegRemoteServer.KegRemoteServer(self,'',9966)
      self.server.start()

      # load the LCD-UI stuff
      if self.config.getboolean('ui','use_lcd'):
         dev = self.config.get('devices','lcd')
         self.info('main','new LCD at device %s' % dev)
         self.lcd = lcddriver.Display(dev)
         self.ui = lcdui(self.lcd)

         self.keypad_fp = open(self.config.get('ui','keypad_pipe'))
         thread.start_new_thread(self.keypadThread,())
      else:
         self.lcd = Display('/dev/null')
         self.ui = lcdui(self.lcd)

      # init flow meter
      dev = self.config.get('devices','flow')
      self.info('main','new flow controller at device %s' % dev)
      tickmetric = self.config.getint('flow','tick_metric')
      tick_skew = self.config.getfloat('flow','tick_skew')
      self.fc = FlowController.FlowController(dev,ticks_per_liter = tickmetric,tick_skew = tick_skew)
      self.last_fridge_time = 0 # time since fridge event (relay trigger)

      # set up the default 'screen'. for now, it is just a boring standard
      self.main_plate = plate_kegbot_main(self.ui)
      self.ui.setCurrentPlate(self.main_plate)
      self.ui.start()
      self.ui.activity()

      # start the refresh loop, which will keep self.ibs populated with the current onewirenetwork.
      thread.start_new_thread(self.ibRefreshLoop,())
      time.sleep(1.0) # sleep to wait for ibrefreshloop - XXX

      # start the flow controller status monitor
      thread.start_new_thread(self.fcStatusLoop,())
      time.sleep(1.0)

      # start the temperature monitor
      if self.config.getboolean('thermo','use_thermo'):
         self.tempsensor = TempMonitor.TempSensor(self.config.get('devices','thermo'))
         self.tempmon = TempMonitor.TempMonitor(self,self.tempsensor,self.QUIT)
         self.tempmon.start()

   def setsigs(self):
      signal.signal(signal.SIGHUP, self.handler)
      signal.signal(signal.SIGINT, self.handler)
      signal.signal(signal.SIGQUIT,self.handler)
      signal.signal(signal.SIGTERM, self.handler)

   def handler(self,signum,frame):
      self.quit()

   def quit(self):
      self.info('main','attempting to quit')

      # hacks for blocking threads..
      self.server.stop()
      self.fc.getStatus()
      if self.config.getboolean('sounds','use_sounds'):
         self.sounds.quit()

      # other quitting
      self.QUIT.set()
      self.ui.stop()

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
         self.main_plate.setFreezer('on ')
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
         self.main_plate.setFreezer('off')
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
         time.sleep(0.5)

         # remove any tokens from the 'idle' list. assume the config value
         # ib_idle_min_disconnected is set to 5 seconds. require each kicked
         # button to have been seen 5 or more seconds ago. (eg, not seen in
         # last 5 seconds).
         cutoff = time.time() - self.config.getint('timing','ib_idle_min_disconnected')
         self.timed_out = [x for x in self.timed_out if self.lastSeen(x) > cutoff]

         # now get down to business.
         try:
            username = self.drinker_queue.get_nowait()
            self.info('flow','api call to start user for %s' % username)
            uid = self.user_store.getUid(username)
            user = self.user_store.getUser(uid)
            self.handleFlow(user)
            continue
         except Queue.Empty:
            pass
         except:
            continue
         for ib in self.ibs:
            if self.key_store.knownKey(ib.read_id()) and ib.read_id() not in self.timed_out:
               time_since_seen = time.time() - self.lastSeen(ib.read_id())
               ceiling = self.config.getfloat('timing','ib_missing_ceiling')
               if time_since_seen < ceiling:
                  self.info('flow','found an authorized ibutton: %s' % ib.read_id())

                  # note: break call at the end of this block ensures that,
                  # after a flow is handled, this mainEventLoop re-starts with
                  # fresh data (eg self.ibs)
                  self.fc.getStatus()
                  time.sleep(0.1)
                  self.handleFlow(ib)
                  break

   def handleDrinker(self,username):
      self.drinker_queue.put_nowait(username)
      return 1

   def stopFlow(self):
      self.STOP_FLOW = 1
      return 1

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
      user_screen = self.makeUserScreen(current_user)
      self.ui.setCurrentPlate(user_screen,replace=1)

      # - turn on flow
      self.fc.openValve()

      # - wait for ibutton release OR inaction timeout
      self.info('flow','starting flow for user %s' % current_user.getName())
      STOP_FLOW = 0

      idle_timeout = self.config.getfloat('timing','ib_idle_timeout')
      ceiling = self.config.getfloat('timing','ib_missing_ceiling')

      # set up the record for logging
      rec = DrinkRecord(self.drink_store,current_user.id,current_keg)

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

            user_screen.write_dict['progbar'].setProgress(self.fc.ticksToOunces(flow_ticks)/8.0)
            user_screen.write_dict['ounces'].setData(oz[:6])

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
      self.ui.setCurrentPlate(self.main_plate,replace=1)

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
      bac = instantBAC(current_user,current_keg,flow_ticks)
      bac += decomposeBAC(old_drink[0],time.time()-old_drink[1])
      rec.emit(flow_ticks,current_grant,grant_ticks,bac)

      ounces = round(self.fc.ticksToOunces(flow_ticks),1)
      self.main_plate.setLastDrink(current_user.getName(),ounces)
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

   def makeUserScreen(self,user):
      scr = lcdui.plate_std(self.ui)

      namestr = "hello %s" % user.getName()
      while len(namestr) < 16:
         if len(namestr)%2 == 0:
            namestr = namestr + ' '
         else:
            namestr = ' ' + namestr
      namestr = namestr[:16]

      line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("| %s |"%namestr,      row=1,col=0,scroll=0)
      progbar = lcdui.widget_progbar(row = 2, col = 2, prefix ='[', postfix=']', proglen = 9)
      #line3 = lcdui.widget_line_std("| [              ] |",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      pipe1 = lcdui.widget_line_std("|", row=2,col=0,scroll=0,fat=0)
      pipe2 = lcdui.widget_line_std("|", row=2,col=19,scroll=0,fat=0)
      ounces = lcdui.widget_line_std("", row=2,col=12,scroll=0,fat=0)

      scr.updateObject('line1',line1)
      scr.updateObject('line2',line2)
      scr.updateObject('progbar',progbar)
      scr.updateObject('pipe1',pipe1)
      scr.updateObject('pipe2',pipe2)
      scr.updateObject('ounces',ounces)
      scr.updateObject('line4',line4)

      return scr

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


# ui stuff
# the next sections of code contain UI widgets and plates used by the main keg
# class.
#
class plate_kegbot_main(lcdui.plate_multi):
   def __init__(self,owner):
      lcdui.plate_multi.__init__(self,owner)
      self.owner = owner

      self.maininfo, self.tempinfo, self.freezerinfo  = lcdui.plate_std(owner), lcdui.plate_std(owner), lcdui.plate_std(owner)
      self.lastinfo, self.drinker  = lcdui.plate_std(owner), lcdui.plate_std(owner)

      self.main_menu = lcdui.plate_select_menu(owner,header="kegbot menu")
      self.main_menu.insert(("show history",None,()))
      self.main_menu.insert(("add user",None,()))
      self.main_menu.insert(("squelch user",None,()))
      self.main_menu.insert(("lock kegbot",None,()))
      #self.main_menu.insert(("exit",owner.setCurrentPlate,(self,)))

      self.cmd_dict = {'right': (self.owner.setCurrentPlate,(self.main_menu,)) }

      line1 = lcdui.widget_line_std(" ================== ",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("      kegbot!!      ",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("  have good beer!!  ",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std(" ================== ",row=3,col=0,scroll=0)

      self.maininfo.updateObject('line1',line1)
      self.maininfo.updateObject('line2',line2)
      self.maininfo.updateObject('line3',line3)
      self.maininfo.updateObject('line4',line4)

      line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("| current temp:    |",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("| unknown          |",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.tempinfo.updateObject('line1',line1)
      self.tempinfo.updateObject('line2',line2)
      self.tempinfo.updateObject('line3',line3)
      self.tempinfo.updateObject('line4',line4)

      line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("| freezer status:  |",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("| [off]            |",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.freezerinfo.updateObject('line1',line1)
      self.freezerinfo.updateObject('line2',line2)
      self.freezerinfo.updateObject('line3',line3)
      self.freezerinfo.updateObject('line4',line4)

      line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("| last pour:       |",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("| 0.0 oz           |",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.lastinfo.updateObject('line1',line1)
      self.lastinfo.updateObject('line2',line2)
      self.lastinfo.updateObject('line3',line3)
      self.lastinfo.updateObject('line4',line4)

      line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("| last drinker:    |",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("| unknown          |",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.drinker.updateObject('line1',line1)
      self.drinker.updateObject('line2',line2)
      self.drinker.updateObject('line3',line3)
      self.drinker.updateObject('line4',line4)

      self.addPlate("main",self.maininfo)
      self.addPlate("temp",self.tempinfo)
      self.addPlate("freezer",self.freezerinfo)
      self.addPlate("last",self.lastinfo)
      self.addPlate("drinker",self.drinker)

      # starts the rotation
      self.rotate_time = 5.0

   def setTemperature(self,tempc):
      inside = "%.1fc/%.1ff" % (tempc,toF(tempc))
      line3 = lcdui.widget_line_std("%s"%inside,row=2,col=0,prefix="| ", postfix= " |", scroll=0)
      self.tempinfo.updateObject('line3',line3)

   def setFreezer(self,status):
      inside = "[%s]" % status
      line3 = lcdui.widget_line_std("%s"%inside,row=2,col=0,prefix="| ", postfix= " |", scroll=0)
      self.freezerinfo.updateObject('line3',line3)

   def setLastDrink(self,user,ounces):
      line3 = lcdui.widget_line_std("%s oz"%ounces,row=2,col=0,prefix ="| ",postfix=" |",scroll=0)
      self.lastinfo.updateObject('line3',line3)
      line3 = lcdui.widget_line_std("%s"%user,row=2,col=0,prefix ="| ",postfix=" |",scroll=0)
      self.drinker.updateObject('line3',line3)

   def gotKey(self,key):
      lcdui.plate_multi.gotKey(self,key)

# start a new kehbot instance, if we are called from the command line
if __name__ == '__main__':
   if flags.daemon:
      daemonize()
   else:
      print "Running in foreground"
   KegBot()
