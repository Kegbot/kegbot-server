import logging
import os
import random
import select
import sys
import threading
import time
import traceback

import Interfaces

class Kegboard(threading.Thread):
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

   class KBRelay(Interfaces.IRelay):
      def __init__(self, kboard, relay_num):
         self.kboard = kboard
         self.relay_num = relay_num

      def Enable(self):
         return self.kboard.EnableRelay(self.relay_num)

      def Disable(self):
         return self.kboard.DisableRelay(self.relay_num)

      def Status(self):
         return self.kboard.RelayStatus(self.relay_num)

   def __init__(self, dev, logger=None, rate=115200):
      threading.Thread.__init__(self)
      self.QUIT = threading.Event()

      # provide interfaces for other components
      self.i_relay_0 = Kegboard.KBRelay(self, 0)
      self.i_relay_1 = Kegboard.KBRelay(self, 1)
      self.i_thermo = self
      self.i_flowmeter = self

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
      self._last_ticks = 0

      self._devpipe = open(dev,'w+',0) # unbuffered is zero
      try:
         os.system("stty %s raw < %s" % (self.rate, self.dev))
      except:
         self.logger.error("error setting raw")

      self._devpipe.flush()
      self.i_relay_0.Disable()
      self.i_relay_1.Disable()

   def run(self):
      self.statusLoop()

   def stop(self):
      self.QUIT.set()

   def _DoCmd(self, cmd):
      self._lock.acquire()
      self._devpipe.write(cmd)
      self._lock.release()

   def EnableRelay(self, num):
      cmd = {0: self.CMD_VALVEON, 1: self.CMD_FRIDGEON}[num]
      self._DoCmd(cmd)
      self.logger.info('relay %i enabled' % num)

   def DisableRelay(self, num):
      cmd = {0: self.CMD_VALVEOFF, 1: self.CMD_FRIDGEOFF}[num]
      self._DoCmd(cmd)
      self.logger.info('relay %i disabled' % num)

   def RelayStatus(self, num):
      status = {0: self.status.valve, 1: self.status.fridge}[num]
      return status

   def GetTemperature(self):
      if self.status:
         return self.status.temp
      else:
         return None

   def GetTicks(self):
      return self.total_ticks

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
      self.logger.info('got status: %s' % str(self.status))
      return self.status

   def GetStatus(self):
      self._DoCmd(self.CMD_STATUS)

   def UpdateTemp(self):
      self._DoCmd(self.CMD_READTEMP)

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
      self.valve = pkt[1]
      self.fridge = pkt[2]

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
      return '<StatusPacket: ticks=%i fridge=%s valve=%s temp=%.04f>' % (self.ticks,
            self.fridge, self.valve, self.temp)

