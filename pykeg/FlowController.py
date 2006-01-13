import os
import random
import select
import threading
import time
import traceback

class FlowController(threading.Thread):
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
   def __init__(self,dev,logger,rate=115200):
      threading.Thread.__init__(self)
      self.QUIT = threading.Event()

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
      self.dev = dev
      self.rate = rate
      self._lock = threading.Lock()
      self.logger = logger
      self.total_ticks = 0
      self.last_fridge_time = 0

      self._devpipe = open(dev,'w+',0) # unbuffered is zero
      try:
         os.system("stty %s raw < %s" % (self.rate, self.dev))
         pass
      except:
         self.logger.error("error setting raw")
         pass

      self._devpipe.flush()
      self.valve_open = None
      self.disableFridge()
      #self.closeValve()
      #self.clearTicks()

   def run(self):
      self.statusLoop()

   def stop(self):
      self.QUIT.set()
      self.getStatus() # hack to break the blocking wait

   def fridgeStatus(self):
      return self.status.fridge

   def readTicks(self):
      return self.total_ticks

   def openValve(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_VALVEON)
      self._lock.release()

   def closeValve(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_VALVEOFF)
      self._lock.release()

   def enableFridge(self):
      if time.time() - self.last_fridge_time < 300:
         self.logger.warn('fridge ON event requested too soon; ignoring')
         return
      self.last_fridge_time = time.time()
      self._lock.acquire()
      self._devpipe.write(self.CMD_FRIDGEON)
      self._lock.release()

   def disableFridge(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_FRIDGEOFF)
      self._lock.release()

   def recvPacket(self):
      #self._lock.acquire()
      fd = self._devpipe.fileno()

      # gobble up ending boundary
      c = os.read(fd,2)
      if c != "M:":
         self.logger.info("no message start found, gobbling")
         while 1:
            c = os.read(fd,1)
            if c != '\n':
               continue
            else:
               #self._lock.release()
               self.logger.info("end of bad packet; returning")
               return

      # now, c should contain the start of a packet
      pkt = os.read(fd,7)
      #self._lock.release()
      self.status = StatusPacket(map(ord,pkt))
      self.total_ticks += self.status.ticks
      return self.status

   def getStatus(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_STATUS)
      self._lock.release()

   def statusLoop(self):
      """ asynchronous fetch loop for the flow controller """
      timeout=0.1
      try:
         self.logger.info('status loop starting')
         self.getStatus()
         while not self.QUIT.isSet():
            (rr,wr,xr) = select.select([self._devpipe],[],[],0.0)
            if len(rr):
               try:
                  p = self.recvPacket()
                  self.logger.info('read status packet ' + str(p))
               except:
                  self.logger.warning('packet read error')
                  traceback.print_exc()
            time.sleep(timeout)
         self.logger.info('status loop exiting')
      except:
         traceback.print_exc()

class StatusPacket:
   FRIDGE_OFF = 0
   FRIDGE_ON = 1
   FRIDGE_UNKNOWN = 2

   VALVE_CLOSED = 0
   VALVE_OPEN = 1

   def __init__(self, pkt):
      self.ticks = pkt[3]*256 + pkt[4]
      self.fridge = pkt[1]
      self.valve = pkt[2]

   def ValveOpen(self):
      return self.valve == self.VALVE_OPEN

   def ValveClosed(self):
      return self.valve == self.VALVE_CLOSED

   def FridgeOn(self):
      return self.fridge == self.FRIDGE_ON

   def FridgeOff(self):
      return self.fridge == self.FRIDGE_OFF

   def __str__(self):
      return '<StatusPacket: ticks=%i fridge=%s valve=%s>' % (self.ticks, self.fridge, self.valve)

class FlowSimulator:
   """ a fake flowcontroller that pours a slow drink """

   def __init__(self):
      self.fridge = 0
      self.valve = 0
      self.ticks = 0
      self.open_time = 0

   def start(self): pass

   def stop(self): pass

   def fridgeStatus(self):
      return self.fridge

   def readTicks(self):
      return int(50*(time.time() - self.open_time))

   def openValve(self):
      self.valve = 1
      self.open_time = time.time()

   def closeValve(self):
      self.valve = 0

   def enableFridge(self):
      self.fridge = 1

   def disableFridge(self):
      self.fridge = 0
