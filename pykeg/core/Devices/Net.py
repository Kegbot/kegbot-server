import logging
import socket
import struct
import threading
import time

from pykeg.core import Interfaces


class KegBoard(threading.Thread,
      Interfaces.IFlowmeter):

   MCAST_ADDR = "224.107.101.103"
   MCAST_PORT = 9012
   def __init__(self):
      threading.Thread.__init__(self)
      self.setDaemon(True)

      self.QUIT = threading.Event()
      self._lock = threading.Lock()
      self.logger = logging.getLogger('netkegboard')

      # provide interfaces for other components
      self._total_ticks = 0

   def run(self):
      self._StatusLoop()

   def stop(self):
      self.QUIT.set()

   def _StatusLoop(self):
      """ Device service loop """
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      sock.bind(('', self.MCAST_PORT))
      mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_ADDR), socket.INADDR_ANY)
      sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

      self.logger.info('listening on %s:%s' % (self.MCAST_ADDR, self.MCAST_PORT))

      last_reading = None
      while not self.QUIT.isSet():
        try:
          val = int(struct.unpack('!I', sock.recv(1024)[:4])[0])
        except ValueError:
          continue

        if last_reading is None or last_reading > val:
          last_reading = val
          continue
        elif last_reading == val:
          continue
        else:
          self._total_ticks += (val - last_reading)
          last_reading = val

   ### public functions

   ### IFlowmeter interfaces

   def GetTicks(self):
      return self._total_ticks


class NetThermo(threading.Thread,
      Interfaces.IFlowmeter):

  MCAST_ADDR = "224.107.101.103"
  MCAST_PORT = 9013
  def __init__(self):
    threading.Thread.__init__(self)
    self.setDaemon(True)
    self.logger = logging.getLogger('netthermo')

    self._last_value = 0
    self._last_time = None

  def SensorName(self):
    return "netthermo"

  def GetTemperature(self):
    return (self._last_value/1000.0, self._last_time)

  def run(self):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', self.MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_ADDR), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    self.logger.info('listening on %s:%s' % (self.MCAST_ADDR, self.MCAST_PORT))

    while True:
      try:
        val = int(struct.unpack('!I', sock.recv(128)[:4])[0])
      except ValueError:
        continue

      self._last_time = time.time()
      if val != self._last_value:
        self._last_value = val


class NetAuth(threading.Thread,
      Interfaces.IAuthDevice):

  MCAST_ADDR = "224.107.101.103"
  MCAST_PORT = 9014
  def __init__(self):
    threading.Thread.__init__(self)
    self.setDaemon(True)
    self.logger = logging.getLogger('netauth')

    self._authed_users = []
    self._user_cache = {}

  def AuthorizedUsers(self):
    return self._authed_users

  def run(self):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', self.MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_ADDR), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    self.logger.info('listening on %s:%s' % (self.MCAST_ADDR, self.MCAST_PORT))

    while True:
      bytes = sock.recv(2048)
      self._authed_users = bytes.split()

