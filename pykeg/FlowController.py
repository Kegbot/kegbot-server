import logging
import os
import random
import select
import sys
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
         gets. note that a status packet is automatically sent periodically

      VALVEON (0x83)
         turn the solenoid valve on. caution: the watchdog timer for the valve
         is not present in the current FC revision, so care must be taken to
         disable the valve when finished.

      VALVEOFF (0x84)
         disable (close) the solenoid valve.

      FRIDGEON (0x90)
         activate the freezer relay, powering on the freezer

      FRIDGEOFF (0x91)
         disable the freezer by pulsing the relay off

      READTEMP (0x93)
         request the controller to refresh temperature data. note a refresh is
         automatically triggered and reported periodically

   STATUS PACKET
      the FC will periodically send a status packet to the host via rs232.
      because there is no easy way to timestamp these on the FC side, it is
      important that the serial queue be kept flushed and current.

      fields are divided by a single space character, and the packet ends with
      the "\r\n" sequence (invidible below)

      here is a sample packet:
         M: S off on 893 26.5

      descriptions of fields:
         "M:"  -  start of message from controller; never changes
         "S"   -  type of controller message; currently only "S" (status) is
                  defined
         "off" -  relay 0 status
         "on"  -  relay 1 status
         893   -  monotonically increasing tick counter; rolls over every
                  2560000 ticks
         26.5  -  temperature in degrees C
   """
   # command         hex        char
   CMD_STATUS      = '\x53'   # 'S'
   CMD_VALVEON     = '\x56'   # 'V'
   CMD_VALVEOFF    = '\x76'   # 'v'
   CMD_FRIDGEON    = '\x46'   # 'F'
   CMD_FRIDGEOFF   = '\x66'   # 'f'
   CMD_READTEMP    = '\x54'   # 'T'

   def __init__(self, dev, logger=None, rate=115200):
      threading.Thread.__init__(self)
      self.QUIT = threading.Event()

      # other stuff
      self.dev = dev
      self.rate = rate
      self._lock = threading.Lock()
      if not logger:
         logger = logging.getLogger('FlowController')
         hdlr = logging.StreamHandler(sys.stdout)
         logger.addHandler(hdlr)
         logger.setLevel(logging.DEBUG)
      self.logger = logger

      self.status = None
      self.total_ticks = 0
      self.last_fridge_time = 0
      self._last_ticks = 0

      self._devpipe = open(dev,'w+',0) # unbuffered is zero
      try:
         os.system("stty %s raw < %s" % (self.rate, self.dev))
      except:
         self.logger.error("error setting raw")

      self._devpipe.flush()
      self.disableFridge()
      self.closeValve()
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
      #if time.time() - self.last_fridge_time < 300:
      #   self.logger.warn('fridge ON event requested too soon; ignoring')
      #   return
      self.last_fridge_time = time.time()
      self._lock.acquire()
      self._devpipe.write(self.CMD_FRIDGEON)
      self._lock.release()

   def updateTemp(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_READTEMP)
      self._lock.release()

   def disableFridge(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_FRIDGEOFF)
      self._lock.release()

   def recvPacket(self):
      line = self._devpipe.readline()
      if line == '':
         self.logger.error('ERROR: Flow device went away; exiting!')
         sys.exit(1)
      if not line.startswith('M: '):
         if line.startswith('K'):
            self.logger.info('Found board: %s' % line[:-2])
         else:
            self.logger.info('no start of packet; ignoring!')
         return None
      if not line.endswith('\r\n'):
         self.logger.info('bad trailer; ignoring!')
         return None
      fields = line[3:-2].split()
      if len(fields) < StatusPacket.NUM_FIELDS:
         self.logger.info('not enough fields; ignoring!')
      self.status = StatusPacket(fields)
      diff = self.status.ticks - self._last_ticks
      if diff < 0:
         self.logger.warn('tick delta from last packet is negative')
      else:
         self.total_ticks += diff
      self._last_ticks = self.status.ticks
      return self.status

   def getStatus(self):
      self._lock.acquire()
      self._devpipe.write(self.CMD_STATUS)
      self._lock.release()

   def statusLoop(self):
      """ asynchronous fetch loop for the flow controller """
      try:
         self.logger.info('status loop starting')
         while not self.QUIT.isSet():
            rr, wr, xr = select.select([self._devpipe],[],[],1.0)
            if len(rr):
               p = self.recvPacket()
         self.logger.info('status loop exiting')
      except:
         self.logger.error('packet read error')
         traceback.print_exc()


class StatusPacket:
   NUM_FIELDS = 5
   FRIDGE_OFF = 'off'
   FRIDGE_ON = 'on'

   VALVE_CLOSED = 'off'
   VALVE_OPEN = 'on'

   def __init__(self, pkt):
      self.temp = float(pkt[4])
      self.ticks = int(pkt[3])
      self.fridge = pkt[1]
      self.valve = pkt[2]

   def _ConvertTemp(self, msbyte, lsbyte):
      # XXX: assuming 12 bit mode
      val = (msbyte & 0x7)*256 + lsbyte
      val = val * 0.0625
      if msbyte >> 3 != 0:
         val = -1 * val
      return val

   def ValveOpen(self):
      return self.valve == self.VALVE_OPEN

   def ValveClosed(self):
      return self.valve == self.VALVE_CLOSED

   def FridgeOn(self):
      return self.fridge == self.FRIDGE_ON

   def FridgeOff(self):
      return self.fridge == self.FRIDGE_OFF

   def __str__(self):
      return '<StatusPacket: ticks=%i fridge=%s valve=%s temp=%.04f>' % (self.ticks, self.fridge, self.valve, self.temp)


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
      return max(0, int(50*(time.time() - self.open_time)))

   def openValve(self):
      self.valve = 1
      self.open_time = time.time()

   def closeValve(self):
      self.valve = 0

   def enableFridge(self):
      self.fridge = 1

   def disableFridge(self):
      self.fridge = 0
