import os,threading

class FC2:
   """
   represents the embedded flowmeter counter microcontroller.
   
   the controller board communicates via rs232. communication to the controller
   consists of single-byte command packets. currently the following commands
   are defined:

      STATUS (0x81)
         cause the FC to send a status packet back to us the next chance it
         gets. note that a status packet is automatically sent after every
         other command.

      VALVEON (0x83)
         turn the solenoid valve on. caution: the watchdog timer for the valve
         is not present in the current FC revision, so care must be taken to
         disable the valve when finished.

      VALVEOFF (0x84)
         disable (close) the solenoid valve.

      PUSHTICKS (0x87)
         enable pushing of flow ticks. in the future, this will cause the FC to
         give priority to the pulse counting ISR, and disable things that might
         interfere with it (ie, temperature reading.) currently does nothing.

      NOPUSHTICKS (0x88)
         return the FC to normal state; the inverse of PUSHTICKS

      FRIDGEON (0x90)
         activate the freezer relay, powering on the freezer

      FRIDGEOFF (0x91)
         disable the freezer by pulsing the relay off

      READTEMP (0x93)
         read the current temperature of the connected sensor. currently does
         nothing, and will probably be removed (as the status packet should
         show this info).

   STATUS PACKET

      the FC will periodically send a status packet to the host via rs232.
      because there is no easy way to timestamp these on the FC side, it is
      important that the serial queue be kept flushed and current.

      the status packet has the following format:

      BYTE  VALUE    Description
      0     "M"      First of the two-bye start sequence
      1     ":"      Second char of the two-byte start sequence
      2     0-255    Packet type. Currently only defined packet is status (0x1)
      3     0-2      Fridge status (0=off, 1=on, 2=unknown)
      4     0-1      Solenoid status (0=off, 1=on)
      5     0-255    High flow ticks (1/4 actual)
      6     0-255    Low flow ticks (1/4 actual)
      7     "\r"     First of two-byte end sequence
      8     "\n"     Second of two-byte end sequence

      the status packet is 9 bytes long, bounded by "M:...\r\n". packets
      failing this simple size and boundary check qill be discarded
   
   """
   def __init__(self,dev,rate=115200,ticks_per_liter=1100,tick_skew=1.0):

      # commands
      self.CMD_STATUS      = '\x81'
      self.CMD_VALVEON     = '\x83'
      self.CMD_VALVEOFF    = '\x84'
      self.CMD_PUSHTICKS   = '\x87'
      self.CMD_NOPUSHTICKS = '\x88'
      self.CMD_FRIDGEON    = '\x90'
      self.CMD_FRIDGEOFF   = '\x91'
      self.CMD_READTEMP    = '\x93'

      # other stuff
      self.UNKNOWN = True
      self.dev = dev
      self.rate = rate
      self.ticks_per_liter = ticks_per_liter
      self.tick_skew = tick_skew
      self._lock = threading.Lock()

      self.status = {"fridge": 2, "valve": 2, "ticks":0}

      self._devpipe = open(dev,'w+',0) # unbuffered is zero
      try:
         os.system("stty %s raw < %s" % (self.rate, self.dev))
         pass
      except:
         print "error setting raw"
         pass

      self._devpipe.flush()
      self.valve_open = None
      self.disableFridge()
      #self.closeValve()
      #self.clearTicks()

   def ticksToOunces(self,ticks):
      # one liter is 32 ounces.
      ticks_per_ounce = float(self.ticks_per_liter)/32.0
      return ticks/ticks_per_ounce

   def ouncesToTicks(self,oz):
      # one liter is 32 ounces.
      ticks_per_ounce = float(self.ticks_per_liter)/32.0
      return oz*ticks_per_ounce

   # helpers for FC1 compatibility
   def fridgeStatus(self):
      return self.status['fridge'] == 1

   def readTicks(self):
      return self.status['ticks']*self.tick_skew

   def openValve(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_VALVEON)
      self._lock.release()
      self.valve_open = True

   def closeValve(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_VALVEOFF)
      self._lock.release()
      self.valve_open = False

   def enableFridge(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_FRIDGEON)
      self._lock.release()
      self.fridge_status = True

   def disableFridge(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_FRIDGEOFF)
      self._lock.release()
      self.fridge_status = False

   def recvPacket(self):
      #self._lock.acquire()
      fd = self._devpipe.fileno()

      # gobble up ending boundary
      c = os.read(fd,2)
      if c != "M:":
         print "no message start found, gobbling"
         while 1:
            c = os.read(fd,1)
            if c != '\n':
               continue
            else:
               #self._lock.release()
               print "end of bad packet; returning"
               return

      # now, c should contain the start of a packet
      pkt = os.read(fd,7)
      #self._lock.release()
      pkt = map(ord,pkt)

      #print "got status packet: %s" % (str(pkt),)
      self.status['fridge'] = pkt[1]
      self.status['valve']  = pkt[2]
      newticks = pkt[3]*256 + pkt[4]
      #newticks *= 4
      self.status['ticks'] += newticks*self.tick_skew
      return pkt

   def getStatus(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_STATUS)
      self._lock.release()

