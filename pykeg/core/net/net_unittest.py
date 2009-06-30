#!/usr/bin/env python

"""Unittest for kegnet module"""

import asyncore
import unittest

from protobufrpc.synchronous import Proxy
from protobufrpc.synchronous import TcpChannel
from pykeg.core.net import net
from pykeg.core import util
from pykeg.core.net.proto import unittest_pb2

class TestService(unittest_pb2.TestService):
  def ToLower(self, rpc_controller, request, done):
    reply = unittest_pb2.TestMessage()
    reply.data = request.data.lower()
    done(reply)

  def ToUpper(self, rpc_controller, request, done):
    reply = unittest_pb2.TestMessage()
    reply.data = request.data.upper()
    done(reply)


class NetTestCase(unittest.TestCase):
  def setUp(self):
    self._thr = net.PumpThread('pump')
    self._thr.start()

  def tearDown(self):
    self._thr.Quit()

  def testBasicUse(self):
    test_service = TestService()
    local_addr = ('', 0)
    server = net.ProtobufRpcServer(local_addr, test_service)
    server.StartServer()

    bound_addr = server.getsockname()

    channel = TcpChannel(bound_addr)
    proxy = Proxy(unittest_pb2.TestService_Stub(channel))

    request = unittest_pb2.TestMessage()
    request.data = "Hello!"

    ret = proxy.TestService.ToLower(request)[0]
    self.assertEquals(ret.data, request.data.lower())

    ret = proxy.TestService.ToUpper(request)[0]
    self.assertEquals(ret.data, request.data.upper())
