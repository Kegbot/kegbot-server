# keg control system
# by mike wakerly; mike@wakerly.com

import os, time
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
from SQLStores import *
from SQLHandler import *
from FlowController import *
from TempMonitor import *

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

      # load the db info, because we will use it often enough
      self.dbhost = self.config.get('DB','host')
      self.dbuser = self.config.get('DB','user')
      self.dbdb = self.config.get('DB','db')
      self.dbpassword = self.config.get('DB','password')
      self.logtable = self.config.get('Logging','logtable')

      # set up logging, using the python 2.3 logging module
      self.main_logger = self.makeLogger('main',logging.INFO)

      # set up the drink, user, and key stores. these classes provide read,
      # write, and search access to information that the keg needs to know
      # about.

      # rather than retyping this stuff on each init line, just add this tuple
      # and the table name to form the init tuple
      db_tuple = (self.dbhost,self.dbuser,self.dbpassword,self.dbdb)

      self.drink_store   = DrinkStore( db_tuple, self.config.get('DB','drink_table') )
      self.user_store    = UserStore( db_tuple, self.config.get('DB','user_table') )
      self.key_store     = KeyStore( db_tuple, self.config.get('DB','key_table') )
      self.policy_store  = PolicyStore( db_tuple, self.config.get('DB','policy_table') )
      self.grant_store   = GrantStore( db_tuple, self.config.get('DB','grant_table') , self.policy_store)
      self.keg_store     = KegStore( db_tuple, self.config.get('DB','keg_table') )
      self.thermo_store  = ThermoStore( db_tuple, self.config.get('DB','thermo_table') )

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
      self.fc = FlowController(flowdev)

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
      self._allibs = []
      self.last_refresh = 0.0
      self.ibs_seen = {} # store time when IB was last seen
      thread.start_new_thread(self.ibRefreshLoop,())
      time.sleep(1.0) # sleep to wait for ibrefreshloop - XXX

      # start the temperature monitor
      if self.config.getboolean('Thermo','use_thermo'):
         self.tempsensor = TempSensor(self.config.get('Thermo','device'))
         self.tempmon = TempMonitor(self,self.tempsensor,self.QUIT)
         self.tempmon.start()

      # start the aim bot
      sn = self.config.get('AIM','screenname')
      pw = self.config.get('AIM','password')
      self.aimbot = KegAIMBot(sn,pw,self)
      self.bm.addBot(self.aimbot,"aimbot",go=0)
      if self.config.getboolean('AIM','use_aim'):
         self.bm.botGo("aimbot")

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

   def makeLogger(self,compname,level=logging.INFO):
      """ set up a logging logger, given the component name """
      ret = logging.getLogger(compname)
      ret.setLevel(level)

      # add sql handler
      if self.config.getboolean('Logging','use_sql'):
         try:
            hdlr = SQLHandler(self.dbhost,self.dbuser,self.dbdb,self.logtable,self.dbpassword)
            formatter = SQLVerboseFormatter()
            hdlr.setFormatter(formatter)
            ret.addHandler(hdlr)
         except:
            ret.warning("Could not start SQL Handler")

      # add a file-output handler
      if self.config.getboolean('Logging','use_logfile'):
         hdlr = logging.FileHandler(self.config.get('Logging','logfile'))
         formatter = logging.Formatter(self.config.get('Logging','logformat',raw=1))
         hdlr.setFormatter(formatter)
         ret.addHandler(hdlr)

      # add tty handler
      if self.config.getboolean('Logging','use_stream'):
         hdlr = logging.StreamHandler(sys.stdout)
         formatter = logging.Formatter(self.config.get('Logging','logformat',raw=1))
         hdlr.setFormatter(formatter)
         ret.addHandler(hdlr)

      return ret

   def tempMonitor(self):
      # XXX --- DEPRECATED --- USE TEMPMON --- XXX #
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
      for target in self._allibs:
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

         if temp != self.last_temp:
            self.log('tempmon','temperature now read as: %s F / %s C' % (self.toF(temp),temp) )
            self.last_temp = temp
            self.last_temp_time = time.time()
            self.main_plate.setTemperature(temp,self.toF(temp))
      self.log('tempMonitor','quit!')


   def toF(self,t):
      """
      convert celcius temperature to fahrenheit.
      """
      return ((9.0/5.0)*t) + 32

   def enableFreezer(self):
      if self.fc.fridgeStatus() == False: 
         self.log('tempmon','activated freezer')
         self.main_plate.setFreezer('on ')
         self.fc.enableFridge()

   def disableFreezer(self):
      if self.fc.fridgeStatus == True:
         self.log('tempmon','disabled freezer')
         self.main_plate.setFreezer('off')
         self.fc.disableFridge()

   def ibRefreshLoop(self):
      """
      Periodically update self.ibs with the current ibutton list.

      Because there are at least two threads (temperature monitor, main event
      loop) that require fresh status of the onewirenetwork, it is useful to
      simply refresh them constantly.
      """
      timeout = self.config.getfloat('Timing','ib_refresh_timeout')
      ignore_ids = self.config.get('Users','ignoreids').split(" ")

      while not self.QUIT.isSet():
         self.netlock.acquire()
         self._allibs = self.ownet.refresh()
         self.netlock.release()
         self.ibs = [ib for ib in self._allibs if ib.read_id() not in ignore_ids]
         self.last_refresh = time.time()
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
         if uib:
            self.handleFlow(uib)

   def handleFlow(self,uib):
      self.ui.activity()
      current_keg = self.keg_store.getCurrentKeg()

      current_user = self.getUser(uib)
      grants = self.grant_store.getGrants(current_user)
      ordered = self.grant_store.orderGrants(grants)

      try:
         current_grant = ordered.pop(0)
      except IndexError:
         self.log('flow','no valid grants found; not starting flow')
         self.timeoutToken(uib.read_id())
         return

      print "current grant: %s" % (current_grant.policy.descr)

      # sequence of steps that should take place:
      # - prepare counter
      self.initFlowCounter()

      # - record flow counter
      initial_flow_ticks = self.fc.readTicks()
      self.log('flow','current flow ticks: %s' % initial_flow_ticks)

      # - turn on UI
      user_screen = self.makeUserScreen(current_user)
      self.ui.setCurrentPlate(user_screen,replace=1)

      # - turn on flow
      self.fc.openValve()
      drink_start = time.time()

      # - wait for ibutton release OR inaction timeout
      self.log('flow','starting flow for user %s' % current_user.getName())
      ib_missing = 0
      STOP_FLOW = 0

      # - start the timout counter
      idle_timeout = self.config.getfloat('Timing','ib_idle_timeout')
      t = threading.Timer(idle_timeout,self.timeoutToken,(uib.read_id(),))
      t.start()

      prog_ticks,last_prog_ticks = 0,0
      ounces,last_ounces = 0.0,-1
      ceiling = self.config.getfloat('Timing','ib_missing_ceiling')

      # set up the record for logging
      rec = DrinkRecord(self.drink_store,current_user.id,current_keg)

      #
      # flow maintenance loop
      #
      last_loop_time = time.time()
      last_flow_time = 0
      ticks,grant_ticks = 0,0
      old_grant = None

      while 1:
         # if we've expired the grant, log it
         if current_grant.isExpired(current_keg.getDrinkOunces(grant_ticks)):
            rec.addFragment(current_grant,grant_ticks)
            grant_ticks = 0
            try:
               current_grant = ordered.pop(0)
               while current_grant.isExpired():
                  current_grant = ordered.pop(0)
            except:
               current_grant = None

         # if no more grants, no more beer
         if not current_grant:
            self.log('flow','no more valid grants; ending flow')
            STOP_FLOW = 1
         else:
            old_grant = current_grant

         # if the token has been gone awhile, end
         time_since_seen = time.time() - self.lastSeen(uib.read_id())
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

         if time.time() - last_flow_time > self.config.getfloat("Flow","polltime"):
            ticks = self.fc.readTicks() - initial_flow_ticks

            last_flow_time = time.time()
            # 1041 ticks = 16 oz
            # 520.5 ticks = 8 oz
            progbars = user_screen.write_dict['progbar'].proglen - 2
            TICKS_PER_8_OZ = self.fc.ouncesToTicks(8.0)
            prog_ticks = (ticks / (TICKS_PER_8_OZ/progbars)) % progbars
            ounces = round(self.fc.ticksToOunces(ticks),1)
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
         #sleep_amt = self.config.getfloat('Timing','ib_verify_timeout')
         #time.sleep(sleep_amt)

      # at this point, the flow maintenance loop has exited. this means
      # we must quickly disable the beer flow and kick the user off the
      # system

      # cancel the idle timeout
      t.cancel()

      # - turn off flow
      self.log('flow','user is gone; flow ending')
      self.fc.closeValve()
      self.ui.setCurrentPlate(self.main_plate,replace=1)

      # - record flow totals; save to user database
      flow_ticks = self.fc.readTicks() - initial_flow_ticks
      rec.addFragment(old_grant,grant_ticks)

      # add the final total to the record
      old_drink = self.drink_store.getLastDrink(current_user.id)
      bac = self.instantBAC(current_user,current_keg,flow_ticks)
      bac += self.decomposeBAC(old_drink[0],time.time()-old_drink[1])
      rec.emit(flow_ticks,current_grant,grant_ticks,bac)

      ounces = round(self.fc.ticksToOunces(flow_ticks),1)
      self.main_plate.setLastDrink(current_user.getName(),ounces)
      self.log('flow','drink tick total: %i' % flow_ticks)

      # - audit the current flow meter reading
      # this amount, self.last_flow_ticks, is used by initFlowCounter.
      # when the next person pours beer, this amount can be compared to
      # the FlowController's tick reading. if the two readings are off by
      # much, then this may be indicitive of a leak, stolen beer, or
      # another serious problem.
      self.last_flow_ticks = flow_ticks
      self.log('flow','flow ended with %s ticks' % flow_ticks)

      # - back to idle UI

   def decomposeBAC(self,bac,seconds_ago):
      rate = 0.02 # rate of loss per hour
      return max(0.0,bac - (rate * (seconds_ago/3600.0)))

   def instantBAC(self,user,keg,drink_ticks):
      # calculate weight in metric KGs
      if user.weight <= 0:
         return 0.0
      kg_weight = user.weight/2.2046
      ounces = keg.getDrinkOunces(drink_ticks)
      #print "BAC for %s-pound (%s-kg) user" % (user.weight,kg_weight)
      #print "for a %s -ounce drink of %s percent alcohol" % (ounces,keg.alccontent)

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
      #print "grams pct: %s" % grams_pct

      # determine how much we've really consumed
      alc_consumed = keg.getDrinkOunces(drink_ticks) * (keg.alccontent/100.0)
      #print "alc consumed = %s" % alc_consumed
      instant_bac = alc_consumed * grams_pct

      #print "BAC: %s" % instant_bac
      return instant_bac

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
      """
      this function is to be called whenever the flow is about to be enabled.

      it may also log any deviation that is noticed.
      """
      if self.last_flow_ticks:
         curr_ticks = self.fc.readTicks()
         if self.last_flow_ticks != curr_ticks:
            self.log('security','last recorded flow count (%s) does not match currently observed flow count (%s)' % (self.last_flow_ticks,curr_ticks))
      self.fc.clearTicks()

   def log(self,component,message):
      self.main_logger.info("%s: %s" % (component,message))

   def beerAccess(self,user):
      """
      determine whether, at this instant, a user may have beer.

      there are several factors that may be checked: what specific permissions
      a user has, based on the date and time; the current keg status and
      whether or not the administrator has blocked access; keg limits (ie,
      maximum beer/pour; hardware fault detection and automatic shutdown.
      """
      return True

   def addUser(self,username,name = None, init_ib = None, admin = 0, email = None,aim = None):
      uid = self.user_store.addUser(username,email,aim)
      self.key_store.addKey(uid,str(init_ib))

class KegShell(threading.Thread):
   def __init__(self,owner):
      threading.Thread.__init__(self)
      self.owner = owner
      self.commands = ['quit','adduser','showlog','hidelog', 'bot']

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

         if cmd == 'bot':
            try:
               subcmd = tokens[1]
               if subcmd == 'go':
                  self.owner.bm.botGo("aimbot")
               elif subcmd == 'stop':
                  self.owner.bm.botStop("aimbot")
               elif subcmd == 'say':
                  user  = tokens[2]
                  msg = raw_input('message: ')
                  self.owner.aimbot.do_SEND_IM(user,msg)
            except:
               pass


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

#
# ui stuff
# the next sections of code contain UI widgets and plates used by the main keg
# class.
#
class plate_kegbot_main(plate_multi):
   def __init__(self,owner):
      plate_multi.__init__(self,owner)
      self.owner = owner

      self.maininfo, self.tempinfo, self.freezerinfo  = plate_std(owner), plate_std(owner), plate_std(owner)
      self.lastinfo, self.drinker  = plate_std(owner), plate_std(owner)

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
      line2 = widget_line_std("| last pour:       |",row=1,col=0,scroll=0)
      line3 = widget_line_std("| 0.0 oz           |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.lastinfo.updateObject('line1',line1)
      self.lastinfo.updateObject('line2',line2)
      self.lastinfo.updateObject('line3',line3)
      self.lastinfo.updateObject('line4',line4)

      line1 = widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = widget_line_std("| last drinker:    |",row=1,col=0,scroll=0)
      line3 = widget_line_std("| unknown          |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

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

   def setTemperature(self,tempc,tempf):
      inside = "%.1fc/%.1ff" % (tempc,tempf)
      line3 = widget_line_std("%s"%inside,row=2,col=0,prefix="| ", postfix= " |", scroll=0)
      self.tempinfo.updateObject('line3',line3)

   def setFreezer(self,status):
      inside = "[%s]" % status
      line3 = widget_line_std("%s"%inside,row=2,col=0,prefix="| ", postfix= " |", scroll=0)
      self.freezerinfo.updateObject('line3',line3)

   def setLastDrink(self,user,ounces):
      line3 = widget_line_std("%s oz"%ounces,row=2,col=0,prefix ="| ",postfix=" |",scroll=0)
      self.lastinfo.updateObject('line3',line3)
      line3 = widget_line_std("%s"%user,row=2,col=0,prefix ="| ",postfix=" |",scroll=0)
      self.drinker.updateObject('line3',line3)

# start a new kehbot instance, if we are called from the command line
if __name__ == '__main__':
   KegBot(config)
