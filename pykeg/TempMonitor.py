import os,threading
import time

class TempMonitor(threading.Thread):
   def __init__(self,owner,sensor,quit_ev):
      threading.Thread.__init__(self)

      self.owner = owner # the KEgBot instance
      self.sensor = sensor # the TempSensor Quolz sensor
      self.QUIT = quit_ev # event to kill us

   def run(self):
      max_low = self.owner.config.getfloat('Thermo','temp_max_low')
      max_high = self.owner.config.getfloat('Thermo','temp_max_high')
      timeout = self.owner.config.getfloat('Thermo','logging_timeout')
      sensor = self.owner.config.getint('Thermo','main_sensor')
      last_temp = -100.0
      last_time = 0
      while not self.QUIT.isSet():
         self.sensor.takeReading()

         currtemp,rectime = self.sensor.getTemp(sensor)

         if currtemp:
            if currtemp >= max_high:
               #self.owner.enableFreezer()
               pass
            elif currtemp <= max_low:
               #self.owner.disableFreezer()
               pass

            if time.time() - last_time > timeout:
               self.owner.log('tempmon','temperature now read as: %s'%currtemp)
               self.owner.thermo_store.logTemp(currtemp, sensor)
               last_time = rectime

class TempSensor:
   """ represents the embedded flowmeter counter microcontroller. """
   def __init__(self,dev,rate=2400):

      self.dev = dev
      self.rate = rate

      self._temps  = {}
      self._times  = {}
      self._version = "unknown"

      self._devpipe = open(dev,'w+',0) # unbuffered is zero

      try:
         os.system("stty %s raw < %s" % (self.rate, self.dev))
         pass
      except:
         print "error setting raw"
         pass

      self._devpipe.flush()

   def getTemp(self, sensor):
      if not self._times.has_key(sensor):
         return (None,None)
      else:
         return (self._temps[sensor],self._times[sensor])

   def takeReading(self):

      # gobble up the boundary characters
      while 1:
         c = self._devpipe.read(1)
         if c == '\r' or c == '\n':
            continue
         else:
            break

      # handle the reset string
      if c == 'R':
         vers = ""
         c = self._devpipe.read(1)
         while c != '\r' and c != '\n':
            c = self._devpipe.read(1)
            vers += c
         self._version = vers

      # otherwise, grab the sensor data string
      else:
         # chomp space (or ignore corrupt/misaligned packet)
         space = self._devpipe.read(1)
         if space != ' ': return

         amt = self._devpipe.read(7)
         self._temps[int(c)] = float(amt)
         self._times[int(c)] = time.time()

