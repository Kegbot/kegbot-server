import os,threading

class FlowController:
   """ represents the embedded flowmeter counter microcontroller. """
   def __init__(self,dev,rate=115200,ticks_per_liter=2200, commands = ('\x81','\x82','\x83','\x84','\x85','\x86','\x90','\x91','\x92')):
      self.dev = dev
      self.rate = rate
      self.ticks_per_liter = 2200
      self._lock = threading.Lock()

      self.fridge_status = False

      self.read_cmd,self.clear_cmd,self.open_cmd,self.close_cmd, self.timer_cmd, self.status_cmd, self.fridgeon_cmd, self.fridgeoff_cmd, self.fridgestatus_cmd = commands[:9]

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

   def valveStatus(self):
      try:
         self._lock.acquire()
         self._devpipe.write(self.status_cmd)
         # XXX - add a timer here, in case read failed
         status = self._devpipe.read(1)
         self._lock.release()
         status = ord(high)*256 + ord(low)
         # returns two-byte string, like '\x01\x00'
      except:
         pass
      return status == '\x01'

   def enableFridge(self):
      self._lock.acquire()
      self._devpipe.write(self.fridgeon_cmd)
      self._lock.release()
      self.fridge_status = True

   def disableFridge(self):
      self._lock.acquire()
      self._devpipe.write(self.fridgeoff_cmd)
      self._lock.release()
      self.fridge_status = False

   def fridgeStatus(self):
      if 1:
         return self.fridge_status
      try:
         raise
         self._lock.acquire()
         self._devpipe.write(self.fridgestatus_cmd)
         # XXX - add a timer here, in case read failed
         status = self._devpipe.read(1)
         self._lock.release()
         status = ord(high)*256 + ord(low)
         # returns two-byte string, like '\x01\x00'
      except:
         return False
      return status == '\x01'

   def readTimer(self):
      try:
         self._lock.acquire()
         self._devpipe.write(self.timer_cmd)
         # XXX - add a timer here, in case read failed
         ticks = self._devpipe.read(3)
         self._lock.release()
         low,mid,high = ticks[0],ticks[1],ticks[2]
         ticks = ord(high)*256 + ord(low)
         # returns two-byte string, like '\x01\x00'
      except:
         ticks = 0
      return "%i %i %i" % (ord(high), ord(mid), ord(low))

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


