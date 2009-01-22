import logging
import re
import select
import socket
import struct
import threading
import time

from pykeg.core import Interfaces
from pykeg.core import kb_threads
from pykeg.core import models

KB2_FLOW_1_RE = re.compile('.*flow_0=(?P<meterval>\d+).*')

class KegBoard(kb_threads.KegbotThread,
      Interfaces.IFlowmeter):

   MCAST_ADDR = "224.107.101.103"
   MCAST_PORT = 9012
   def __init__(self):
      kb_threads.KegbotThread.__init__(self, 'netkegboard')
      self._total_ticks = 0

   def run(self):
      """ Device service loop """
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      sock.bind(('', self.MCAST_PORT))
      mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_ADDR), socket.INADDR_ANY)
      sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

      self._logger.info('listening on %s:%s' % (self.MCAST_ADDR, self.MCAST_PORT))

      last_reading = None
      while not self._quit:
        rr, wr, er = select.select([sock], [], [], 0.5)
        if not rr:
          continue
        buf = sock.recv(1024)
        val = None

        m = KB2_FLOW_1_RE.match(buf)
        if m:
          try:
            val = int(m.group(1))
          except ValueError:
            pass
        else:
          try:
            val = int(struct.unpack('!I', buf[:4])[0])
          except ValueError:
            pass

        if val is None:
          continue

        if last_reading is None or last_reading > val:
          last_reading = val
          continue
        elif last_reading == val:
          continue
        else:
          self._total_ticks += (val - last_reading)
          last_reading = val

      self._logger.info('server exiting')
      sock.close()

   ### public functions

   ### IFlowmeter interfaces

   def GetTicks(self):
      return self._total_ticks


class NetThermo(kb_threads.KegbotThread,
      Interfaces.IFlowmeter):

  MCAST_ADDR = "224.107.101.103"
  MCAST_PORT = 9013
  def __init__(self):
    KegbotThread.__init__(self, 'netthermo')
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
    self._logger.info('listening on %s:%s' % (self.MCAST_ADDR, self.MCAST_PORT))

    while True:
      try:
        val = int(struct.unpack('!I', sock.recv(128)[:4])[0])
      except ValueError:
        continue

      self._last_time = time.time()
      if val != self._last_value:
        self._last_value = val


class NetAuth(kb_threads.KegbotThread,
      Interfaces.IAuthDevice):

  MCAST_ADDR = "224.107.101.103"
  MCAST_PORT = 9014
  def __init__(self):
    kb_threads.KegbotThread.__init__(self, 'netauth')
    self._authed_users = []
    self._user_cache = {}

  def _HandlePacket(self, bytes):
    users = set()
    ids = bytes.split()
    for tok in ids:
      tokstr = tok.replace('0x', '')
      q = models.Token.objects.filter(keyinfo__exact=tokstr)
      if len(q):
        users.add(q[0].user.username)
    self._authed_users = users

  def AuthorizedUsers(self):
    return self._authed_users

  @classmethod
  def MakeServerSocket(cls):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', cls.MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(cls.MCAST_ADDR), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

  @classmethod
  def MakeClientSocket(cls):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.connect((cls.MCAST_ADDR, cls.MCAST_PORT))
    return sock

  def run(self):
    sock = NetAuth.MakeServerSocket()
    self._logger.info('listening on %s:%s' % (self.MCAST_ADDR, self.MCAST_PORT))

    while not self._quit:
      rr, wr, er = select.select([sock], [], [], 0.5)
      if not rr:
        continue
      bytes = sock.recv(2048)
      self._HandlePacket(bytes)
