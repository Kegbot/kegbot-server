# Copyright 2008 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Kegnet protocol library.

The module wraps the protocol-buffer implementation of the kegnet communication
protocol.
"""

import logging

from protobufrpc.synchronous import Proxy
from protobufrpc.synchronous import TcpChannel

from pykeg.core.net import net
from pykeg.core.net import service
from pykeg.core.net.proto import kegnet_pb2

class KegnetError(Exception):
  """Generic error for kegnet module."""


class UnknownMessageError(Exception):
  """Message type or ID is not known."""


class KegnetClient:
  def __init__(self, addr, name):
    self._addr = addr
    self._name = name
    self._channel = TcpChannel(self._addr)
    self._proxy = Proxy(kegnet_pb2.Core_Stub(self._channel))
    self._handle = kegnet_pb2.ClientHandle()

  def Login(self):
    request = self._handle
    request.client_name = self._name
    res = self._proxy.Core.Login(request)
    self._handle = res[0]

  def FlowUpdate(self, name, amt):
    request = kegnet_pb2.MeterReading()
    request.handle.MergeFrom(self._handle)
    request.name = name
    request.value = amt
    self._proxy.Core.PostMeterReading(request)

  def StartFlow(self, tap_name):
    request = kegnet_pb2.TapRequest()
    request.handle.MergeFrom(self._handle)
    request.tap_info.name = tap_name
    self._proxy.Core.StartFlow(request)

  def StopFlow(self, tap_name):
    request = kegnet_pb2.TapRequest()
    request.handle.MergeFrom(self._handle)
    request.tap_info.name = tap_name
    self._proxy.Core.StopFlow(request)


class KegnetServer(net.ProtobufRpcServer):
  def __init__(self, name, kb_env, addr):
    self._logger = logging.getLogger(name)
    self._kb_env = kb_env
    self._logger.info('Starting up.')
    services = (
        service.CoreService('CoreService', kb_env),
    )
    net.ProtobufRpcServer.__init__(self, addr, *services)
