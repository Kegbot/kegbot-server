# Copyright 2009 Mike Wakerly <opensource@hoho.com>
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

"""Network RPC client/server implementation."""

import asyncore
import asynchat
import socket
import cStringIO
import logging
import struct

from protobufrpc import common as protobufrpc_common
from protobufrpc import protobufrpc_pb2

from pykeg.core import event
from pykeg.core import util


class PumpThread(util.KegbotThread):
  def run(self):
    while not self._quit:
      asyncore.loop(timeout=0.5, count=1)


class ProtobufRpcServer(asyncore.dispatcher):
  """An asyncore server implementation of protobuf-rpc."""
  def __init__(self, addr, *services):
    self._bind_address = addr
    self._qsize = 5
    self._services = {}
    for service in services:
      self._services[service.GetDescriptor().name] = service
    asyncore.dispatcher.__init__(self)

  def StartServer(self):
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.set_reuse_addr()
    self.bind(self._bind_address)
    self.listen(self._qsize)

  def StopServer(self):
    self.close()

  def GetRequestObjects(self, strname):
    service_name, method_name = strname.split('.')
    service = self._services[service_name]
    method = service.GetDescriptor().FindMethodByName(method_name)
    request = service.GetRequestClass(method)()
    return service, method, request

  ### asyncore.dispatcher methods

  def handle_accept(self):
    try:
      conn, addr = self.accept()
    except socket.error:
      raise
    except TypeError:
      raise # ???
    ProtobufRpcHandler(self, conn)


class ProtobufRpcHandler(asynchat.async_chat):
  """Asyncore hander implementation that understands protobuf-rpc messages."""
  _HEADER_FORMAT = "!I"
  def __init__(self, server, sock=None, map=None):
    asynchat.async_chat.__init__(self, sock, map)
    self._server = server
    self.set_terminator(struct.calcsize(self._HEADER_FORMAT))
    self._have_header = False
    self._ibuffer = cStringIO.StringIO()

  ### async_chat methods
  def collect_incoming_data(self, data):
    self._ibuffer.write(data)

  def found_terminator(self):
    strbuf = self._ibuffer.getvalue()
    if not self._have_header:
      self._have_header = True
      message_len = struct.unpack(self._HEADER_FORMAT, strbuf[:4])[0]
      self.set_terminator(message_len)
      return

    # Reset for next message
    self._have_header = False
    self.set_terminator(struct.calcsize(self._HEADER_FORMAT))
    self._ibuffer.seek(0)
    self._ibuffer.truncate()

    self.string_received(strbuf)

  def string_received(self, data):
    rpc = protobufrpc_pb2.Rpc()
    rpc.ParseFromString( data )
    for serializedRequest in rpc.request:
      service, method, request = self._server.GetRequestObjects(serializedRequest.method)
      request.ParseFromString( serializedRequest.serialized_request )
      controller = protobufrpc_common.Controller()

      class callbackClass( object ):
        def __init__( self ):
          self.response = None
        def __call__( self, response ):
          self.response = response

      callback = callbackClass()
      service.CallMethod( method, controller, request, callback )
      responseRpc = self.serialize_rpc( self.serialize_response( callback.response, serializedRequest ) )
      self._SendPackedResponse(responseRpc)

  def _SendPackedResponse(self, message):
    bytes = message.SerializeToString()
    buflen = len(bytes)
    ret = struct.pack('!I', buflen) + bytes
    self.push(ret)

  def serialize_response( self, response, serializedRequest ):
    serializedResponse = protobufrpc_pb2.Response()
    serializedResponse.id = serializedRequest.id
    serializedResponse.serialized_response = response.SerializeToString()
    return serializedResponse

  def serialize_rpc( self, serializedResponse ):
    rpc = protobufrpc_pb2.Rpc()
    rpcResponse = rpc.response.add()
    rpcResponse.serialized_response = serializedResponse.serialized_response
    rpcResponse.id = serializedResponse.id
    return rpc


