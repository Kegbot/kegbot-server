import os,threading
import time

class TempMonitor(threading.Thread):
   def __init__(self,owner,sensor,quit_ev):
      threading.Thread.__init__(self)

      self.owner = owner # the KEgBot instance
      self.sensor = sensor # the TempSensor Quolz sensor
      self.QUIT = quit_ev # event to kill us

   def run(self):
      max_low = self.owner.config.getfloat('thermo','temp_max_low')
      max_high = self.owner.config.getfloat('thermo','temp_max_high')
      timeout = self.owner.config.getfloat('thermo','logging_timeout')
      sensor = self.owner.config.getint('thermo','main_sensor')
      lasttemp = -100.0
      last_time = 0
      while not self.QUIT.isSet():
         self.sensor.takeReading()
         currtemp,rectime = self.sensor.getTemp(sensor)

         if currtemp:
            if currtemp >= max_high:
               self.owner.enableFreezer()
            elif currtemp <= max_low:
               self.owner.disableFreezer()

            self.owner.main_plate.setTemperature(currtemp)
            if time.time() - last_time > timeout:
               if currtemp != lasttemp:
                  fs = 0
                  if self.owner.fc.fridgeStatus():
                     fs = 1
                  self.owner.thermo_store.logTemp(currtemp, sensor, fs)
                  lasttemp = currtemp
               else:
                  self.owner.thermo_store.updateLastTemp()

               last_time = rectime

class TempSensor:
   """
   class for decoding output from a quozl temperature sensor.

   despite the confusing name, the tempsensor class does NOT represent a DS1820
   temperature sensor. it represents the quozl PIC device, which may have up to
   4 DS1820 sensors connected.
   """
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

      # get rid of any data in the serial buffer; i'm only interested in the
      # most recent temperature
      self._devpipe.flush()

   def getTemp(self, sensor):
      """
      return the temperature of a particular sensor, as the tuple (temperature,
      time recorded)

      if a sensor has not been seen, or if the sensor number is invalid, a
      tuple of (None,0) is returned).
      """
      if not self._times.has_key(sensor):
         return (None,0)
      else:
         return (self._temps[sensor],self._times[sensor])

   def takeReading(self):
      """
      read one line (one temperature reading) from the quozl sensor.

      sensor readings are sent continuously to the serial port, seperated by
      \r\n and some spaces between fields. if a line is corrupt (or the
      decoding is out of alignment), no reading is taken. 

      the first line the sensor sends on power-up is its version string. this
      qill be read and saved if encountered.
      """
      # gobble up the boundary characters
      while 1:
         c = self._devpipe.read(1)
         if c == '\r' or c == '\n':
            continue
         else:
            break

      # handle the power-on reset/info string
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

         # we believe c contains a sensor number (0-4), but things could still
         # be misaligned. test.
         try:
            c = int(c)
         except:
            return

         amt = self._devpipe.read(7)
         try:
            self._temps[c] = float(amt)
            self._times[c] = time.time()
         except:
            return

