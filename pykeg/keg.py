# keg control system
# by mike wakerly; mike@wakerly.com

import os, cPickle, time
from onewirenet import *
from ibutton import *
from mtxorb import *
from lcdui import *
from output import *
from ConfigParser import ConfigParser
import thread, threading
import signal

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

      # used for auditing between pours. see comments inline.
      self.last_flow_ticks = None

      self.freezer_status = None
      self.disableFreezer()

      # a list of buttons (probably just zero or one) that have been connected
      # for too long. if in this list, the mainEventLoop will wait for the
      # button to 'go away' for awhile until it will recognize it again.
      self.timed_out = []

      # set up the import stuff: the ibutton onewire network, and the LCD UI
      self.netlock = threading.Lock()
      onewire_dev = self.config.get('UI','onewire_dev')
      self.ownet = onewirenet(onewire_dev)
      self.log('main','new onewire net at device %s' % onewire_dev)
      lcd_dev = self.config.get('UI','lcd_dev')
      self.log('main','new LCD at device %s' % lcd_dev)
      self.lcd = Display(lcd_dev,model=self.config.get('UI','lcd_model'))
      self.ui = lcdui(self.lcd)

      # restore the databases
      self.loadDBs()

      # init flow meter
      flowdev = self.config.get('Flow','flowdev')
      self.log('main','new flow controller at device %s' % flowdev)
      self.flowmeter = FlowController(flowdev)

      # set up the default 'screen'. for now, it is just a boring standard
      # plate. but soon we will define a custom cycling plate..
      #self.main_plate = plate_std(self.ui)
      self.main_plate = plate_kegbot_main(self.ui)
      #line1 = widget_line_std("*------------------*",row=0,col=0,scroll=0)
      #line2 = widget_line_std("|     kegbot!!     |",row=1,col=0,scroll=0)
      #line3 = widget_line_std("| by mike wakerly! |",row=2,col=0,scroll=0)
      #line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)
      #self.main_plate.updateObject('line1',line1)
      #self.main_plate.updateObject('line2',line2)
      #self.main_plate.updateObject('line3',line3)
      #self.main_plate.updateObject('line4',line4)
      self.ui.setCurrentPlate(self.main_plate)
      self.ui.start()
      self.ui.activity()

      thread.start_new_thread(self.tempMonitor,())

      self.mainEventLoop()

   def setsigs(self):
      signal.signal(signal.SIGHUP, self.handler)
      signal.signal(signal.SIGINT, self.handler)
      signal.signal(signal.SIGQUIT,self.handler)
      signal.signal(signal.SIGTERM, self.handler)

   def handler(self,signum,frame):
      self.quit()

   def quit(self):
      self.QUIT.set()
      self.ui.stop()
      self.saveDBs()

   def loadDBs(self):
      """ populate the internal representations of users, etc, based on a
      previously saved execution. """

      try:
         user_file = open(self.config.get('DB','user_file'),'w+')
         self.user_db = cPickle.Unpickler(user_file).load()
         user_file.close()
      except EOFError:
         self.user_db = {}

      try:
         token_file = open(self.config.get('DB','token_file'),'w+')
         self.token_db = cPickle.Unpickler(token_file).load()
         token_file.close()
      except EOFError:
         self.token_db = {}

      try:
         grant_file = open(self.config.get('DB','grant_file'),'w+')
         self.grant_db = cPickle.Unpickler(grant_file).load()
         grant_file.close()
      except EOFError:
         self.grant_db = {}

      try:
         history_file = open(self.config.get('DB','history_file'),'w+')
         self.history_db = cPickle.Unpickler(history_file).load()
         history_file.close()
      except EOFError:
         self.history_db = History()

      admin_uname = self.config.get('Admin','username')
      admin_ib = self.config.get('Admin','ib_id')
      if not self.user_db.has_key(admin_uname):
         self.addUser(username = admin_uname,init_ib = admin_ib, admin = 1)
         #self.user_db[admin_uname] = User(admin_uname,admin=1)
         #self.token_db[admin_ib] = Token(admin_ib,admin_uname)

   def saveDBs(self):
      user_file = open(self.config.get('DB','user_file'),'w')
      cPickle.Pickler(user_file).dump(self.user_db)
      user_file.close()

      grant_file = open(self.config.get('DB','grant_file'),'w')
      cPickle.Pickler(grant_file).dump(self.grant_db)
      grant_file.close()

      token_file = open(self.config.get('DB','token_file'),'w')
      cPickle.Pickler(token_file).dump(self.token_db)
      token_file.close()

      history_file = open(self.config.get('DB','history_file'),'w')
      cPickle.Pickler(history_file).dump(self.history_db)
      history_file.close()

   def tempMonitor(self):
      temp_ib = self.config.get('Thermo','temperature_ib_id')
      timeout = self.config.getfloat('Thermo','reading_timeout')
      max_low = self.config.getfloat('Thermo','temp_max_low')
      max_high = self.config.getfloat('Thermo','temp_max_high')
      max_variation = self.config.getfloat('Thermo','max_variation')
      max_bogus = self.config.getint('Thermo','max_bogus')

      temp,last_temp = -100.0, -100.0
      bogus_count = 0
      bogus_temp = 1
      last_reading_time = 0
      while not self.QUIT.isSet():
         while time.time() - last_reading_time < timeout:
            if self.QUIT.isSet():
               return
            time.sleep(0.1)
         last_reading_time = time.time()

         # XXX -- need a cleaner way to do this. require some pyonewire revisions
         self.netlock.acquire()
         idx = 0
         for ib in self.ownet.refresh():
            if ib.read_id() == temp_ib:
               count = 0
               while count < 6:
                  ret = self.ownet.ReadTemperature(self.ownet[idx].ID)
                  if not ret:
                     self.log('tempmon',yellow('temperature reading returned zero, retrying'))
                     count = count+1
                     time.sleep(0.1)
                  else:
                     temp = ret
                     break
            idx += 1
         self.netlock.release()
         temp = round(temp,6)

         # deal with a bogus reading
         if abs(temp - last_temp) > max_variation and last_temp != -100.0:
            if temp == 0.0:
               bogus_count += 1
               bogus_temp = temp
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
               self.log('tempmon',yellow('bogus count reset'))
               bogus_count = 0

         # now, decide what to do based on the temperature
         if temp >= max_high:
            self.netlock.acquire()
            self.enableFreezer()
            self.netlock.release()
         elif temp <= max_low:
            self.netlock.acquire()
            self.disableFreezer()
            self.netlock.release()

         if temp != last_temp:
            self.log('tempmon','temperature now read as: %s' % temp)
            last_temp = temp

   def enableFreezer(self):
      if self.freezer_status != 'on':
         cmd = self.config.get('Thermo','fridge_on_cmd')
         os.system(cmd)
         self.freezer_status = 'on'
         self.log('tempmon',green('activated freezer'))

   def disableFreezer(self):
      if self.freezer_status != 'off':
         cmd = self.config.get('Thermo','fridge_off_cmd')
         os.system(cmd)
         self.freezer_status = 'off'
         self.log('tempmon',green('disabled freezer'))

   def mainEventLoop(self):
      last_refresh = 0
      while 1:
         time.sleep(0.5)
         if self.QUIT.isSet():
            return

         # XXX - this bit is necessary, because calls to refresh are _very_
         # expensive: it appears that all threads block while python makes a
         # C-level call. this is unfortunate. i think there is a way to make
         # the ownet call 'unblock' threads; will see..
         # XXX - update: fixed? added Py_BEGIN_ALLOW_THREADS macros around owFirst, owNext
         if time.time() - last_refresh >= 0.6:
            self.netlock.acquire()
            ibs = self.ownet.refresh()
            self.netlock.release()
            last_refresh = time.time()
         uib = None

         # remove any tokens from the 'idle' list
         present = [x.read_id() for x in ibs]
         for kicked in self.timed_out:
            if not kicked in present:
               self.log('flow','removed %s from timeout list' % kicked)
               self.timed_out.remove(kicked)

         # now get down to business
         for ib in ibs:
            if self.knownToken(ib) and ib.read_id() not in self.timed_out:
               if ib.verify():
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
            # - record flow counter
            initial_flow_ticks = self.readFlowMeter()
            self.log('flow','current flow ticks: %s' % initial_flow_ticks)

            # - turn on UI
            user_screen = self.makeUserScreen(current_user)
            self.ui.setCurrentPlate(user_screen,replace=1)

            # - prepare counter
            self.initFlowCounter()

            # - turn on flow
            self.enableFlow()

            # - wait for ibutton release OR inaction timeout
            self.log('flow','starting flow for user %s' % current_user.getName())
            ib_missing = 0
            STOP_FLOW = 0

            # handle an idle timeout
            idle_timeout = self.config.getfloat('Timing','ib_idle_timeout')
            t = threading.Timer(idle_timeout,self.timeoutToken,(uib.read_id(),))
            if 1 or not current_user.isAdmin():
               t.start()

            while 1:
               # because of onewirenet glitches, we can define a threshhold for
               # the amount of time we will allow the ibutton to be 'missing'.
               # this amount is set in config->Timing->ib_missing_ceiling and
               # config->Timing->ib_verify_timeout. the product of the two
               # values is a rough estimate of the missing detection speed.
               if not uib.verify():
                  ib_missing += 1
               else:
                  # reset the missing counter, since the ibutton is back
                  ib_missing = 0

               # check other credentials necessary to keep the beer flowing!
               if self.QUIT.isSet():
                  STOP_FLOW = 1

               elif ib_missing >= self.config.getint('Timing','ib_missing_ceiling'):
                  STOP_FLOW = 1

               elif uib.read_id() in self.timed_out:
                  STOP_FLOW = 1

               elif not self.beerAccess(current_user):
                  STOP_FLOW = 1

               if STOP_FLOW:
                  break

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
            self.disableFlow()
            self.ui.setCurrentPlate(self.main_plate,replace=1)

            # - record flow totals; save to user database
            flow_ticks = self.readFlowMeter() - initial_flow_ticks
            if flow_ticks > 0:
               self.history_db.logDrink(current_user,flow_ticks)
               self.log('flow','drink tick total: %s' % flow_ticks)
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

   def knownToken(self,ib):
      return ib.read_id() in self.token_db.keys()

   def getUser(self,ib):
      for id in self.token_db.keys():
         if id == ib.read_id():
            ownerid = self.token_db[id].owner
            return self.user_db[ownerid]

   def readFlowMeter(self):
      ticks = self.flowmeter.readTicks()
      return ticks

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
      line3 = widget_line_std("| [              ] |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

      scr.updateObject('line1',line1)
      scr.updateObject('line2',line2)
      scr.updateObject('line3',line3)
      scr.updateObject('line4',line4)

      return scr

   def enableFlow(self):
      self.flowmeter.openValve()

   def disableFlow(self):
      self.flowmeter.closeValve()

   def debug(self,msg):
      print "[debug] %s" % (msg,)

   def initFlowCounter(self):
      """ this function is to be called whenever the flow is about to be enabled.
      it may also log any deviation that is noticed. """
      if self.last_flow_ticks:
         curr_ticks = self.readFlowMeter()
         if self.last_flow_ticks != curr_ticks:
            self.log('security','last recorded flow count (%s) does not match currently observed flow count (%s)' % (self.last_flow_ticks,curr_ticks))

   def log(self,component,message):
      timelog = time.strftime("%b %d %H:%M:%S", time.localtime())
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

   def addUser(self,username,name = None, init_ib = None, admin = 0, email = None):
      if self.user_db.has_key(username):
         raise
      nuser = User(username,name,admin,email)
      self.user_db[username] = nuser
      if init_ib:
         ntok = Token(init_ib,username)
         self.token_db[init_ib] = ntok

class User:
   def __init__(self,username,name = None,admin = 0,email = None):
      self.username = username
      self.admin = admin
      self.name = name
      self.email = email
      self.active = 1

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

class Token:
   def __init__(self,id,owner,guest = 0):
      self.ID = id
      self.owner = owner
      self.guest = guest

   def isGuestToken(self):
      return self.guest == 1

class History:
   def __init__(self):
      self.STARTED = time.time()
      self.hist = []

   def logDrink(self,user,amt):
      self.hist.append((time.time(),user.getId(),amt))

class Grant:
   """ the basic grant class.
   it provides a getAccess() function, which returns true for all states.
   possible state data to be inspected: date and time, beer keg status, user's
   past debt, etc."""
   def __init__(self,evaltype = "normal"):

      # evaltype: specifies the evaluation priority given to a grant, with
      # respect to its evalAccess function. see the KegBot::BeerAccess routine
      # for more info.
      self.evaltype = evaltype
      self.expired = 0
   
   def evalAccess(self,user,kegbot):
      return user.isActive()

class ExpirationGrant(Grant):
   def __init__(self,exptime):
      Grant.__init__(self)
      self.exptime = exptime

   def evalAccess(self,user,kegbot):
      if Grant.evalAccess(self,user,kegbot):
         if time.time() >= self.exptime:
            self.expired = 1 # auto-expire
         return time.time() < self.exptime

class CalendarGrant(Grant):
   def __init__(self,default = "deny",acllist = None):
      Grant.__init__(self)

   def evalAccess(self,user,kegbot):
      if Grant.evalAccess(self,user,kegbot):
         return 1

class FlowController:
   """ represents the embedded flowmeter counter microcontroller. """
   def __init__(self,dev,rate=115200):
      self.dev = dev
      self.rate = rate
      self._devpipe = open(dev,'w+',0) # unbuffered is zero

      try:
         os.system("stty %s raw < %s" % (self.rate, self.dev))
      except:
         print "error setting raw"
         pass

   def openValve(self):
      self._devpipe.write('\x83')
   
   def closeValve(self):
      self._devpipe.write('\x84')

   def readTicks(self):
      self._devpipe.write('\x81')
      # XXX - add a timer here, in case read failed
      ticks = self._devpipe.read(2)
      low,high = ticks[0],ticks[1]
      ticks = ord(high)*256 + ord(low)
      # returns two-byte string, like '\x01\x00'
      return ticks

   def clearTicks(self):
      self._devpipe.write('\x82')

class plate_kegbot_main(plate_std):
   def __init__(self,owner):
      plate_std.__init__(self,owner)

      self.last_updated = 0

      line1 = widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = widget_line_std("|     kegbot!!     |",row=1,col=0,scroll=0)
      line3 = widget_line_std("| have good beer!! |",row=2,col=0,scroll=0)
      line4 = widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.updateObject('line1',line1)
      self.updateObject('line2',line2)
      self.updateObject('line3',line3)
      self.updateObject('line4',line4)
      
   #def refreshObjects(self,countn):
   #   self.last_updated = time.time()
   #   return plate_std.refreshObjects(self,countn)

if __name__ == '__main__':
   KegBot(config)
