# keg control system
# by mike wakerly; mike@wakerly.com

import os, cPickle, time
import logging
from onewirenet import *
from ibutton import *
from mtxorb import *
from lcdui import *
from output import *
from ConfigParser import ConfigParser
import thread, threading
import signal
import readline
import traceback

from KegRemoteServer import KegRemoteServer
from KegAIMBot import KegAIMBot
from toc import BotManager
from SQLStores import DrinkStore, KeyStore, UserStore
from SQLHandler import *

# edit this line to point to your config file; that's all you have to do!
config = 'keg.cfg'

class KegBot:
   """ the thinking kegerator! """
   def __init__(self,config):

      # first, handle control-C's and stuff
      self.QUIT = threading.Event()
      self.setsigs()

      self.config = ConfigParser()
      self.config.read(config)

      self.verbose = 0

      # used for auditing between pours. see comments inline.
      self.last_flow_ticks = None
      self.freezer = Freezer(self.config)

      # set up logging, using the python 2.3 logging module
      self.main_logger = logging.getLogger('kegbot')
      self.main_logger.setLevel(logging.INFO)

      self.dbhost = self.config.get('DB','host')
      self.dbuser = self.config.get('DB','user')
      self.dbdb = self.config.get('DB','db')
      self.dbpassword = self.config.get('DB','password')
      self.logtable = self.config.get('Logging','logtable')

      # add a file-output handler
      if self.config.getboolean('Logging','use_logfile'):
         hdlr = logging.FileHandler(self.config.get('Logging','logfile'))
         formatter = logging.Formatter(self.config.get('Logging','logformat',raw=1))
         hdlr.setFormatter(formatter)
         self.main_logger.addHandler(hdlr)

      # add tty handler
      if self.config.getboolean('Logging','use_stream'):
         hdlr = logging.StreamHandler(sys.stdout)
         formatter = logging.Formatter(self.config.get('Logging','logformat',raw=1))
         hdlr.setFormatter(formatter)
         self.main_logger.addHandler(hdlr)

      # add sql handler
      if self.config.getboolean('Logging','use_sql'):
         try:
            hdlr = SQLHandler(self.dbhost,self.dbuser,self.dbdb,self.logtable,self.dbpassword)
            formatter = SQLVerboseFormatter()
            hdlr.setFormatter(formatter)
            self.main_logger.addHandler(hdlr)
         except:
            self.main_logger.warning("Could not start SQL Handler")

      # set up the drink, user, and key stores. these classes provide read,
      # write, and search access to information that the keg needs to know
      # about.
      self.drink_store = DrinkStore( (self.dbhost,self.dbuser,self.dbpassword,self.dbdb,self.config.get('DB','drink_table') ))
      self.user_store  = UserStore( (self.dbhost,self.dbuser,self.dbpassword,self.dbdb,self.config.get('DB','user_table') ))
      self.key_store   = KeyStore( (self.dbhost,self.dbuser,self.dbpassword,self.dbdb,self.config.get('DB','key_table') ))

      # a list of buttons (probably just zero or one) that have been connected
      # for too long. if in this list, the mainEventLoop will wait for the
      # button to 'go away' for awhile until it will recognize it again. among
      # other things, this keeps a normally-closed solenoid valve from burning
      # out
      self.timed_out = []

      # start a bot manager for AIM use
      self.bm = BotManager()

      # set up the import stuff: the ibutton onewire network, and the LCD UI
      self.netlock = threading.Lock()
      onewire_dev = self.config.get('UI','onewire_dev')
      try:
         self.ownet = onewirenet(onewire_dev)
         self.log('main','new onewire net at device %s' % onewire_dev)
      except:
         self.log('main','not connected to onewirenet')

      # load the LCD-UI stuff
      if self.config.getboolean('UI','use_lcd'):
         lcd_dev = self.config.get('UI','lcd_dev')
         self.log('main','new LCD at device %s' % lcd_dev)
         self.lcd = Display(lcd_dev,model=self.config.get('UI','lcd_model'))
         self.ui = lcdui(self.lcd)
      else:
         self.lcd = Display('/dev/null')
         self.ui = lcdui(self.lcd)
      self.last_temp = -100.0
      self.last_temp_time = 0

      # init flow meter
      flowdev = self.config.get('Flow','flowdev')
      self.log('main','new flow controller at device %s' % flowdev)
      self.flowmeter = FlowController(flowdev)

      # set up the default 'screen'. for now, it is just a boring standard
      # plate. but soon we will define a custom cycling plate.. (TODO)
      self.main_plate = plate_kegbot_main(self.ui)
      self.ui.setCurrentPlate(self.main_plate)
      self.ui.start()
      self.ui.activity()

      # set up the remote call server, for anything that wants to monitor the keg
      host = self.config.get('Remote','host')
      port = self.config.get('Remote','port')
      #self.cmdserver = KegRemoteServer(self,host,port)
      #self.cmdserver.start()


      self.io = KegShell(self)
      self.io.start()

      # start the refresh loop, which will keep self.ibs populated with the current onewirenetwork.
      self.ibs = []
      self.last_refresh = 0.0
      self.ibs_seen = {} # store time when IB was last seen
      thread.start_new_thread(self.ibRefreshLoop,())
      time.sleep(1.0) # sleep to wait for ibrefreshloop - XXX

      # start the temperature monitor
      if self.config.getboolean('Thermo','use_thermo'):
         thread.start_new_thread(self.tempMonitor,())

      # start the aim bot
      if self.config.getboolean('AIM','use_aim'):
         self.aimBot()
         #thread.start_new_thread(self.aimBot,())

      self.mainEventLoop()

   def setsigs(self):
      signal.signal(signal.SIGHUP, self.handler)
      signal.signal(signal.SIGINT, self.handler)
      signal.signal(signal.SIGQUIT,self.handler)
      signal.signal(signal.SIGTERM, self.handler)

   def handler(self,signum,frame):
      self.quit()

   def quit(self):
      self.log('main','attempting to quit')
      self.QUIT.set()
      self.ui.stop()
      if self.config.getboolean('AIM','use_aim'):
         self.aimbot.saveSessions()
      #self.cmdserver.stop()

   def tempMonitor(self):

      # constants for the monitor
      temp_ib = self.config.get('Thermo','temperature_ib_id')
      timeout = self.config.getfloat('Thermo','reading_timeout')
      max_low = self.config.getfloat('Thermo','temp_max_low')
      max_high = self.config.getfloat('Thermo','temp_max_high')
      max_variation = self.config.getfloat('Thermo','max_variation')
      max_bogus = self.config.getint('Thermo','max_bogus')

      temp,last_temp = -100.0, -100.0
      bogus_count = 0
      last_reading_time = 0

      ib = None
      read_count,found = 0,0

      # get the temperature ibutton. XXX/TODO -- should allow for multiple
      # sensors and read from the net in a sane way.
      for target in self.ibs:
         if target.read_id() == temp_ib:
            ib = target

      if not ib:
         self.log('tempmon','could not find temperature sensor, aborting monitor')
         return
      else:
         self.log('tempmon','got sensor..')

      while not self.QUIT.isSet():
         while time.time() - last_reading_time < timeout:
            if self.QUIT.isSet():
               return
            time.sleep(0.1)
         last_reading_time = time.time()

         # XXX -- need a cleaner way to do this. require some pyonewire revisions
         self.netlock.acquire()
         count = 0
         while count < 6:
            ret = ib.readTemperature()
            if not ret:
               self.log('tempmon','temperature reading returned zero, retrying')
               count = count+1
               time.sleep(0.1)
            else:
               temp = ret
               break
         self.netlock.release()
         temp = round(temp,6)

         # deal with a bogus reading
         if abs(temp - self.last_temp) > max_variation and self.last_temp != -100.0:
            if temp == 0.0:
               bogus_count += 1
               msg = bold(red('read bogus temperature: ')) + red(str(temp))
               self.log('tempmon',msg)
               if bogus_count >= max_bogus:
                  self.log('tempmon',bold(red('bogus readings exceed maximum of %s; current reading of %s now valid' %(max_bogus,temp))))
                  bogus_count = 0
               else:
                  continue
            else:
               self.log('tempmon',bold(red('strange temperature read, not treating as bogus: %s'% temp)))
         else:
            if bogus_count > 0:
               self.log('tempmon','bogus count reset')
               bogus_count = 0

         # now, decide what to do based on the temperature
         if temp >= max_high:
            self.enableFreezer()
         elif temp <= max_low:
            self.disableFreezer()

         self.log('tempmon','temperature now read as: %s F / %s C' % (self.toF(temp),temp) )
         if temp != self.last_temp:
            self.last_temp = temp
            self.last_temp_time = time.time()
            self.main_plate.setTemperature(temp,self.toF(temp))
      self.log('tempMonitor','quit!')


   def toF(self,t):
      """
      convert celcius temperature to fahrenheit.
      """
      return ((9.0/5.0)*t) + 32

   def aimBot(self):
      sn = self.config.get('AIM','screenname')
      pw = self.config.get('AIM','password')
      self.aimbot = KegAIMBot(sn,pw,self)
      self.bm.addBot(self.aimbot,"aimbot")

   def enableFreezer(self):
      if self.freezer.getStatus() != 'on':
         self.log('tempmon','activated freezer')
      self.freezer.enable()

   def disableFreezer(self):
      if self.freezer.getStatus() != 'off':
         self.log('tempmon','disabled freezer')
      self.freezer.disable()

   def ibRefreshLoop(self):
      """
      Periodically update self.ibs with the current ibutton list.

      Because there are at least two threads (temperature monitor, main event
      loop) that require fresh status of the onewirenetwork, it is useful to
      simply refresh them constantly.
      """
      timeout = self.config.getfloat('Timing','ib_refresh_timeout')
      while not self.QUIT.isSet():
         self.netlock.acquire()
         self.ibs = self.ownet.refresh()
         self.last_refresh = time.time()
         self.netlock.release()
         for ib in self.ibs:
            self.ibs_seen[ib.read_id()] = self.last_refresh
         time.sleep(timeout)
      self.log('ibRefreshLoop','quit!')

   def lastSeen(self,ibname):
      if self.ibs_seen.has_key(ibname):
         return self.ibs_seen[ibname]
      else:
         return 0

   def mainEventLoop(self):
      last_refresh = 0
      while not self.QUIT.isSet():
         time.sleep(0.5)
         uib = None

         # remove any tokens from the 'idle' list
         present = [x.read_id() for x in self.ibs]
         for kicked in self.timed_out:
            if not kicked in present:
               self.log('flow','removed %s from timeout list' % kicked)
               self.timed_out.remove(kicked)

         # now get down to business
         for ib in self.ibs:
            if self.knownKey(ib.read_id()) and ib.read_id() not in self.timed_out:
               time_since_seen = time.time() - self.lastSeen(ib.read_id()) 
               ceiling = self.config.getfloat('Timing','ib_missing_ceiling')
               if time_since_seen < ceiling:
                  self.log('flow','found an authorized ibutton: %s' % ib.read_id())
                  uib = ib
                  break

         # enter this block if we have a recognized iButton. note that above
         # code will stop with the first authorized ibutton. 
         if uib:
            self.ui.activity()

            current_user = self.getUser(uib)
            #grants = self.getGrants(uib.ID)

            # sequence of steps that should take place:
            # - prepare counter
            self.initFlowCounter()

            # - record flow counter
            initial_flow_ticks = self.flowmeter.readTicks()
            self.log('flow','current flow ticks: %s' % initial_flow_ticks)

            # - turn on UI
            user_screen = self.makeUserScreen(current_user)
            self.ui.setCurrentPlate(user_screen,replace=1)

            # - turn on flow
            self.flowmeter.openValve()

            # - wait for ibutton release OR inaction timeout
            self.log('flow','starting flow for user %s' % current_user.getName())
            ib_missing = 0
            STOP_FLOW = 0

            # handle an idle timeout
            idle_timeout = self.config.getfloat('Timing','ib_idle_timeout')
            t = threading.Timer(idle_timeout,self.timeoutToken,(uib.read_id(),))
            if 1 or not current_user.isAdmin():
               t.start()

            prog_ticks,last_prog_ticks = 0,0
            ounces,last_ounces = 0.0,0.0
            last_missing = time.time()
            while 1:
               time_since_seen = time.time() - self.lastSeen(uib.read_id()) 
               ceiling = self.config.getfloat('Timing','ib_missing_ceiling')
               if time_since_seen > ceiling:
                  self.log('flow',red('ib went missing, ending flow (%s,%s)'%(time_since_seen,ceiling)))
                  STOP_FLOW = 1

               # check other credentials necessary to keep the beer flowing!
               if self.QUIT.isSet():
                  STOP_FLOW = 1

               elif uib.read_id() in self.timed_out:
                  STOP_FLOW = 1

               elif not self.beerAccess(current_user):
                  STOP_FLOW = 1

               if STOP_FLOW:
                  break

               ticks = self.flowmeter.readTicks() - initial_flow_ticks
               # 1041 ticks = 16 oz
               # 520.5 ticks = 8 oz
               progbars = user_screen.write_dict['progbar'].proglen - 2
               TICKS_PER_8_OZ = self.flowmeter.ouncesToTicks(8.0)
               prog_ticks = (ticks / (TICKS_PER_8_OZ/progbars)) % progbars
               ounces = round(self.flowmeter.ticksToOunces(ticks),1)
               oz = "%s oz" % (ounces,)
               oz = oz + "    "
               if ounces != last_ounces or prog_ticks != last_prog_ticks:
                  user_screen.write_dict['progbar'].progress = (ticks/TICKS_PER_8_OZ) % 1
                  user_screen.write_dict['ounces'].setData(oz[:6])

                  last_prog_ticks = prog_ticks
                  last_ounces = ounces
                  user_screen.refreshAll() # XXX -- is this necessary anymore?

               # otherwise, timeout for a bit before we check all this stuff
               # again
               sleep_amt = self.config.getfloat('Timing','ib_verify_timeout')
               time.sleep(sleep_amt)

            # at this point, the flow maintenance loop has exited. this means
            # we must quickly disable the beer flow and kick the user off the
            # system

            # cancel the idle timeout
            t.cancel()

            # - turn off flow
            self.log('flow','user is gone; flow ending')
            self.flowmeter.closeValve()
            self.ui.setCurrentPlate(self.main_plate,replace=1)

            # - record flow totals; save to user database
            flow_ticks = self.flowmeter.readTicks() - initial_flow_ticks
            if flow_ticks > 0:
               self.drink_store.logDrink(current_user,flow_ticks)
               self.log('flow','drink tick total: %i' % flow_ticks)
            #current_user.addFlowTicks(flow_ticks)

            # - audit the current flow meter reading
            # this amount, self.last_flow_ticks, is used by initFlowCounter.
            # when the next person pours beer, this amount can be compared to
            # the FlowController's tick reading. if the two readings are off by
            # much, then this may be indicitive of a leak, stolen beer, or
            # another serious problem.
            self.last_flow_ticks = flow_ticks
            self.log('flow','flow ended with %s ticks' % flow_ticks)

            # - back to idle UI

   def timeoutToken(self,id):
      self.log('timeout','timing out id %s' % id)
      self.timed_out.append(id)

   def knownKey(self,keyinfo):
      return self.key_store.knownKey(keyinfo)

   def getUser(self,ib):
      key = self.key_store.getKey(ib.read_id())
      if key:
         return self.user_store.getUser(key.getOwner())

   def makeUserScreen(self,user):
      scr = plate_std(self.ui)

      namestr = "hello %s" % user.getName()
      while len(namestr) < 16:
         if len(namestr)%2 == 0:
            namestr = namestr + ' '
         else:
            namestr = ' ' + namestr
      namestr = namestr[:16]

      line1 = widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = widget_line_std("| %s |"%namestr,      row=1,col=0,scroll=0)
      progbar = widget_progbar(row = 2, col = 2, prefix ='[', postfix=']', proglen = 9)
      #line3 = widget_line_std("| [              ] |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

      pipe1 = widget_line_std("|", row=2,col=0,scroll=0,fat=0)
      pipe2 = widget_line_std("|", row=2,col=19,scroll=0,fat=0)
      ounces = widget_line_std("", row=2,col=12,scroll=0,fat=0)

      scr.updateObject('line1',line1)
      scr.updateObject('line2',line2)
      #scr.updateObject('line3',line3)
      scr.updateObject('progbar',progbar)
      scr.updateObject('pipe1',pipe1)
      scr.updateObject('pipe2',pipe2)
      scr.updateObject('ounces',ounces)
      scr.updateObject('line4',line4)

      return scr

   def debug(self,msg):
      print "[debug] %s" % (msg,)

   def initFlowCounter(self):
      """ this function is to be called whenever the flow is about to be enabled.
      it may also log any deviation that is noticed. """
      if self.last_flow_ticks:
         curr_ticks = self.flowmeter.readTicks()
         if self.last_flow_ticks != curr_ticks:
            self.log('security','last recorded flow count (%s) does not match currently observed flow count (%s)' % (self.last_flow_ticks,curr_ticks))
      self.flowmeter.clearTicks()

   def log(self,component,message):
      self.main_logger.info("%s: %s" % (component,message))

   def tty_log(self,component,message):
      timelog = time.strftime("%b %d %H:%M:%S", time.localtime())
      if self.verbose == 1:
         print '%s [%s] %s' % (green(timelog),blue('%8s' % component),message)

   def beerAccess(self,user):
      """ determine whether, at this instant, a user may have beer.

      there are several factors that may be checked: what specific permissions
      a user has, based on the date and time; the current keg status and
      whether or not the administrator has blocked access; keg limits (ie,
      maximum beer/pour; hardware fault detection and automatic shutdown.
      """
      #grants = self.getUserGrants(user)
      #GRANTED = 1

      grants = []
      for grant in grants:
         access = grant.evalAccess(user,self)
         evaltype = grant.evaltype

         if evaltype == 'required':
            if access == 0:
               return 0
         elif evaltype == 'normal':
            if access == 1:
               return 1
      return 1

   def addUser(self,username,name = None, init_ib = None, admin = 0, email = None,aim = None):
      uid = self.user_store.addUser(username,email,aim)
      self.key_store.addKey(uid,str(init_ib))

class KegShell(threading.Thread):
   def __init__(self,owner):
      threading.Thread.__init__(self)
      self.owner = owner
      self.commands = ['quit','adduser','showlog','hidelog']

      # setup readline to do fancy tab completion!
      self.completer = Completer()
      self.completer.set_choices(self.commands)
      readline.parse_and_bind("tab: complete")
      readline.set_completer(self.completer.complete)

   def run(self):
      while 1:
         try:
            input = self.prompt()
            tokens = string.split(input,' ')
            cmd = string.lower(tokens[0])
         except:
            raise

         if cmd == 'quit':
            self.owner.quit()
            return

         if cmd == 'showlog':
            self.owner.verbose = 1

         if cmd == 'hidelog':
            self.owner.verbose = 0

         if cmd == 'adduser':
            user = self.adduser()
            username,admin,aim,initib = user

            print "got user: %s" % str(username)

            try:
               self.owner.addUser(username,init_ib = initib,admin=admin,aim=aim)
               print "added user successfully"
            except:
               print "failed to create user"
               raise

   def prompt(self):
      try:
         prompt = "[KEGBOT] "
         cmd = raw_input(prompt)
      except:
         cmd = ""
      return cmd

   def adduser(self):
      print "please type the unique username for this user."
      username = raw_input("username: ")
      print "will this user have admin privileges?"
      admin = raw_input("admin [y/N]: ")
      print "please type the user's aim name, if known"
      aim = raw_input("aim name [none]: ")
      print "would you like to associate a particular beerkey with this user?"
      print "here are the buttons i see on the network:"
      count = 0
      for ib in self.owner.ibs:
         print "[%i] %s (%s)" % (count,ib.name,ib.read_id())
         count = count+1
      key = raw_input("key number [none]: ")
      try:
         ib = self.owner.ibs[int(key)]
         key = ib.read_id()
         print "selected %s" % key
      except:
         key = None

      if string.lower(admin)[0] == 'y':
         admin = 1
      else:
         admin = 0

      if aim == "" or aim == "\n":
         aim = None

      if key == "" or key == "\n":
         key = None

      return (username,admin,aim,key)


class Completer:
   def __init__(self):
      self.list = []

   def complete(self, text, state):
      if state == 0:
         self.matches = self.get_matches(text)
      try:
         return self.matches[state]
      except IndexError:
         return None

   def set_choices(self, list):
       self.list = list

   def get_matches(self, text):
      matches = []
      for x in self.list:
         if string.find(x, text) == 0:
            matches.append(x)
      return matches

class User:
   def __init__(self,username,name = None,admin = 0,email = None, aim = None):
      self.username = username
      self.admin = admin
      self.name = name
      self.email = email
      self.active = 1
      self.aim = aim

   def getName(self):
      if self.name:
         return self.name
      return self.username

   def getId(self):
      return self.username

   def isAdmin(self):
      return self.admin == 1

   def isActive(self):
      return self.active

class Key:
   def __init__(self,keyinfo,owner_id,guest = 0):
      self.keyinfo = keyinfo
      self.owner_id = owner_id
      self.guest = guest

   def isGuestToken(self):
      return self.guest == 1

class Token:
   def __init__(self,id,owner,guest = 0):
      self.ID = id
      self.owner = owner
      self.guest = guest

   def isGuestToken(self):
      return self.guest == 1

class Freezer:
   def __init__(self,config):
      self.on_cmd = config.get('Thermo','fridge_on_cmd')
      self.off_cmd = config.get('Thermo','fridge_off_cmd')
      self.status = 'unknown'

   def enable(self):
      os.system(self.on_cmd)
      self.status = 'on'
   
   def disable(self):
      os.system(self.off_cmd)
      self.status = 'off'

   def getStatus(self):
      return self.status

class FlowController:
   """ represents the embedded flowmeter counter microcontroller. """
   def __init__(self,dev,rate=115200,ticks_per_liter=2200, commands = ('\x81','\x82','\x83','\x84')):
      self.dev = dev
      self.rate = rate
      self.ticks_per_liter = 2200
      self._lock = threading.Lock()

      self.read_cmd,self.clear_cmd,self.open_cmd,self.close_cmd = commands[:4]

      self._devpipe = open(dev,'w+',0) # unbuffered is zero
      try:
         os.system("stty %s raw < %s" % (self.rate, self.dev))
         pass
      except:
         print "error setting raw"
         pass

      self.valve_open = None
      self.closeValve()
      #self.clearTicks()

   def ticksToOunces(self,ticks):
      # one liter is 32 ounces.
      ticks_per_ounce = float(self.ticks_per_liter)/32.0
      return ticks/ticks_per_ounce

   def ouncesToTicks(self,oz):
      # one liter is 32 ounces.
      ticks_per_ounce = float(self.ticks_per_liter)/32.0
      return oz*ticks_per_ounce

   def openValve(self):
      self._lock.acquire()
      self._devpipe.write(self.open_cmd)
      self._lock.release()
      self.valve_open = True

   def closeValve(self):
      self._lock.acquire()
      self._devpipe.write(self.close_cmd)
      self._lock.release()
      self.valve_open = False

   def readTicks(self):
      try:
         self._lock.acquire()
         self._devpipe.write(self.read_cmd)
         # XXX - add a timer here, in case read failed
         ticks = self._devpipe.read(2)
         self._lock.release()
         low,high = ticks[0],ticks[1]
         ticks = ord(high)*256 + ord(low)
         # returns two-byte string, like '\x01\x00'
      except:
         ticks = 0
      return ticks

   def clearTicks(self):
      self._lock.acquire()
      self._devpipe.write(self.clear_cmd)
      self._lock.release()

class plate_kegbot_main(plate_multi):
   def __init__(self,owner):
      plate_multi.__init__(self,owner)
      self.owner = owner

      self.maininfo, self.tempinfo, self.freezerinfo  = plate_std(owner), plate_std(owner), plate_std(owner)
      self.lastinfo = plate_std(owner)

      line1 = widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = widget_line_std("|     kegbot!!     |",row=1,col=0,scroll=0)
      line3 = widget_line_std("| have good beer!! |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.maininfo.updateObject('line1',line1)
      self.maininfo.updateObject('line2',line2)
      self.maininfo.updateObject('line3',line3)
      self.maininfo.updateObject('line4',line4)

      line1 = widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = widget_line_std("| current temp:    |",row=1,col=0,scroll=0)
      line3 = widget_line_std("| unknown          |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.tempinfo.updateObject('line1',line1)
      self.tempinfo.updateObject('line2',line2)
      self.tempinfo.updateObject('line3',line3)
      self.tempinfo.updateObject('line4',line4)

      line1 = widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = widget_line_std("| freezer status:  |",row=1,col=0,scroll=0)
      line3 = widget_line_std("| [off]            |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.freezerinfo.updateObject('line1',line1)
      self.freezerinfo.updateObject('line2',line2)
      self.freezerinfo.updateObject('line3',line3)
      self.freezerinfo.updateObject('line4',line4)

      line1 = widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = widget_line_std("| freezer status:  |",row=1,col=0,scroll=0)
      line3 = widget_line_std("| [off]            |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.freezerinfo.updateObject('line1',line1)
      self.freezerinfo.updateObject('line2',line2)
      self.freezerinfo.updateObject('line3',line3)
      self.freezerinfo.updateObject('line4',line4)

      line1 = widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = widget_line_std("| last pour:       |",row=1,col=0,scroll=0)
      line3 = widget_line_std("| 16.3 oz          |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.lastinfo.updateObject('line1',line1)
      self.lastinfo.updateObject('line2',line2)
      self.lastinfo.updateObject('line3',line3)
      self.lastinfo.updateObject('line4',line4)

      self.addPlate("main",self.maininfo)
      self.addPlate("temp",self.tempinfo)
      self.addPlate("freezer",self.freezerinfo)
      self.addPlate("last",self.lastinfo)

      # starts the rotation
      self.rotate_time = 5.0

   def setTemperature(self,tempc,tempf):
      inside = "%.1fc/%.1ff" % (tempc,tempf)
      inside += " "*(16-len(inside))
      line3 = widget_line_std("| %s |"%inside,row=2,col=0,scroll=0)
      self.tempinfo.updateObject('line3',line3)

if __name__ == '__main__':
   KegBot(config)
