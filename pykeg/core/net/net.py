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

"""Kegnet client/server implementation."""

import asyncore
import asynchat
import socket
import cStringIO
import logging
import Queue
import struct

from pykeg.core import event
from pykeg.core import kb_common
from pykeg.core import manager
from pykeg.core.net import kegnet
from pykeg.core.net.proto import kegnet_pb2

class KegnetProtocolHandler(asynchat.async_chat):
  """A general purpose request handler for the Kegnet protocol.

  This async_chat subclass can be used for client and server implementations.
  The handler will call _HandleKegnetMessage on receipt of a complete kegnet
  message.

  The method _HandleBadMessage will be called when a malformed message was
  received.
  """
  def __init__(self, sock=None, map=None):
    asynchat.async_chat.__init__(self, sock, map)
    self.set_terminator(5)
    self._have_header = False
    self._ibuffer = cStringIO.StringIO()

  ### async_chat methods
  def collect_incoming_data(self, data):
    self._ibuffer.write(data)

  def found_terminator(self):
    strbuf = self._ibuffer.getvalue()
    if not self._have_header:
      self._have_header = True
      message_len = struct.unpack('<I', strbuf[1:5])[0]
      self.set_terminator(message_len)
      return

    self._have_header = False
    self.set_terminator(5)
    self._ibuffer.seek(0)
    self._ibuffer.truncate()

    if not strbuf:
      self._HandleEmptyMessage()
      return

    try:
      msg = kegnet.msg_from_wire_bytes(strbuf)
      self._HandleKegnetMessage(msg)
      return
    except kegnet.KegnetError, exception:
      self._HandleBadMessage(strbuf, exception)
      return

  def handle_close(self):
    asynchat.async_chat.handle_close(self)
    self._server.ChannelClosed(self)

  ### KegnetProtocolHandler methods
  def _HandleBadMessage(self, strdata, exception):
    pass

  def _HandleEmptyMessage(self):
    pass

  def _HandleKegnetMessage(self, message):
    pass

  def _PushAck(self, success=True):
    msg = kegnet_pb2.StatusReply()
    if success:
      msg.code = msg.OK
    else:
      msg.code = msg.ERROR
    self._PushMessage(msg)

  def _PushMessage(self, msg):
    self.push(kegnet.msg_to_wire_bytes(msg))


class KegnetServerHandler(KegnetProtocolHandler):
  """ An asyncore handler for the core kegnet server. """
  def __init__(self, sock, server):
    KegnetProtocolHandler.__init__(self, sock)
    self._server = server
    self._server.ChannelOpened(self)

  def _HandleBadMessage(self, strdata, exception):
    self._server._logger.warn("Unknown command from %s, closing connection" %
                              str(self.addr))
    self._server._logger.warn("Exception was: %s" % str(exception))
    self._server.ChannelClosed(self)
    self.close()

  def _HandleKegnetMessage(self, message):
    res = self._server.HandleMessage(message, self)
    if res:
      self._PushMessage(res)


class KegnetProtocolClient(KegnetProtocolHandler):
  def __init__(self, addr, map=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.connect(addr)
    KegnetProtocolHandler.__init__(self, sock, map)
    self._response_queue = Queue.Queue()

  def _HandleBadMessage(self, strdata, exception):
    print "bad message"
    self._response_queue.put(None)

  def _HandleEmptyMessage(self, strdata):
    print "empty message!"
    self._response_queue.put(None)

  def _HandleKegnetMessage(self, message):
    print "OK message!"
    print message
    self._response_queue.put(message)

  def SendAsync(self, msg):
    self._PushMessage(msg)

  def SendSync(self, msg, timeout=None):
    self._PushMessage(msg)
    return self.WaitForResponse(timeout)

  def WaitForResponse(self, timeout=None):
    return self._response_queue.get(timeout=timeout)

  ### convenience functions
  def SendConnect(self, name):
    msg = kegnet.Message.ClientConnect(client_name=name)
    self.SendAsync(msg)

  def SendRegisterFlowDevice(self, name):
    msg = kegnet.Message.RegisterFlowDev(name=name)
    self.SendAsync(msg)

  def SendFlowUpdate(self, name, amt):
    msg = kegnet.Message.FlowUpdate(name=name, count=amt)
    self.SendAsync(msg)


class KegnetDevice(object):
  def __init__(self, client, device_type, name):
    self._client = client
    self._device_type = device_type
    self._local_name = name
    self._global_name = ".".join(('kegnet', client.GetName(), self._device_type,
        self._local_name))

  def GetType(self):
    return self._device_type

  def GetLocalName(self):
    """Get the name that the remote client uses."""
    return self._local_name

  def GetGlobalName(self):
    """Get the name used in kbcore registration."""
    return self._global_name


class KegnetFlowDevice(KegnetDevice):
  def __init__(self, client, name):
    KegnetDevice.__init__(self, client, 'flow', name)


class KegnetClientState(object):
  """State holder for a Kegnet client connection"""
  def __init__(self, client_name, client_addr, kb_env):
    self._client_name = client_name
    self._client_addr = client_addr
    self._devices = {
      'flow' : {},
      'relay' : {},
    }
    self._logger = logging.getLogger(':'.join(('kegnet', self._client_name)))
    self._kb_env = kb_env

  def __str__(self):
    return "[%s at %s]" % (self._client_name, self._client_addr)

  def GetName(self):
    return self._client_name

  def _GetDevice(self, device_type, local_name):
    return self._devices.get(device_type, {}).get(local_name)

  def _GetFlowDevice(self, local_name):
    return self._GetDevice('flow', local_name)

  def _RegisterDevice(self, device):
    if isinstance(device, KegnetFlowDevice):
      flow_manager = self._kb_env.GetFlowManager()
      try:
        flow_manager.RegisterDevice(device.GetGlobalName())
      except manager.AlreadyRegisteredError:
        return kegnet.GenericResponse.ALREADY_EXISTS
      self._devices[device.GetType()][device.GetLocalName()] = device
      return kegnet.GenericResponse.OK

    return kegnet.GenericResponse.UNKNOWN_FAILURE

  def Cleanup(self):
    flow_manager = self._kb_env.GetFlowManager()
    for name, device in self._devices['flow'].iteritems():
      self._logger.info('Removing device: %s' % name)
      flow_manager.UnregisterDevice(device.GetGlobalName())

  def RegisterFlowDevice(self, name):
    self._logger.info('Registering new flow device: %s' % (name,))
    device = self._GetFlowDevice(name)
    if device:
      return kegnet.GenericResponse.ALREADY_EXISTS
    flowdev = KegnetFlowDevice(self, name)
    return self._RegisterDevice(flowdev)

  def FlowUpdate(self, name, meter_reading):
    flow_manager = self._kb_env.GetFlowManager()
    device = self._GetFlowDevice(name)

    ev = event.Event(kb_common.KB_EVENT.FLOW_DEV_ACTIVITY)
    ev.device_name = device.GetGlobalName()
    ev.meter_reading = meter_reading
    self._logger.info('Publishing event: %s' % ev)
    self._kb_env.GetEventHub().PublishEvent(ev)

  def FlowEnd(self, name):
    flow_manager = self._kb_env.GetFlowManager()
    device = self._GetFlowDevice(name)
    ev = event.Event(kb_common.KB_EVENT.FLOW_END,
        device_name=device.GetGlobalName())
    self._kb_env.GetEventHub().PublishEvent(ev)


class KegnetServer(asyncore.dispatcher):
  """asyncore server implementation for Kegnet protocol"""
  def __init__(self, name, kb_env, addr='', port=0, qsize=5):
    self._name = name
    self._kb_env = kb_env
    self._logger = logging.getLogger(self._name)
    self._bind_address = (addr, port)
    self._qsize = qsize
    asyncore.dispatcher.__init__(self)

    self._clients_by_name = {}
    self._clients_by_addr = {}

    # Map message classes (types) to internal response handlers.
    self._handlers = {
      kegnet_pb2.RegisterFlowDev: self._HandleRegisterFlowDev,
      kegnet_pb2.UnregisterFlowDev: self._HandleUnregisterFlowDev,
      kegnet_pb2.FlowUpdate: self._HandleFlowUpdate,
      kegnet_pb2.FlowEnd: self._HandleFlowEnd,
      kegnet_pb2.ClientDisconnect: self._HandleClientDisconnect,
    }

  def StartServer(self):
    self._logger.info("Starting server on %s" % str(self._bind_address,))
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.set_reuse_addr()
    self.bind(self._bind_address)
    self.listen(self._qsize)

  def StopServer(self):
    self._logger.info("Stopping server")
    self.close()

  def GetClientFromChannel(self, channel):
    return self._clients_by_addr.get(channel.addr)

  def GetClientFromAddress(self, addr):
    return self._clients_by_addr.get(addr)

  def GetClientFromName(self, name):
    return self._clients_by_name.get(name)

  def ChannelOpened(self, channel):
    self._logger.info('Remote host connected: %s:%i' % channel.addr)

  def ChannelClosed(self, channel):
    """Called by a channel when the connection has closed.

    This routine handles cleanup of a client that is going away.
    """
    self._logger.info('Remote host disconnected: %s:%i' % channel.addr)
    client = self.GetClientFromChannel(channel)
    if client is not None:
      self._RemoveClient(client)

  def _CreateClient(self, client_name, client_addr):
    """ Creates a new client.

    A client is associated with a connection to the server. If the channel dies,
    the client is removed and all devices registered to the client should be
    removed as well.
    """
    self._logger.info('Creating new client "%s"' % client_name)
    client = KegnetClientState(client_name, client_addr, self._kb_env)
    self._clients_by_name[client_name] = client
    self._clients_by_addr[client_addr] = client
    ev = event.Event(kb_common.KB_EVENT.CLIENT_CONNECTED,
        client_name=client_name)
    self._kb_env.GetEventHub().PublishEvent(ev)
    return client

  def _RemoveClient(self, client):
    self._logger.info('Deleting client: %s' % client)
    name = client._client_name
    addr = client._client_addr
    client.Cleanup()
    if name in self._clients_by_name:
      del self._clients_by_name[name]
    if addr in self._clients_by_addr:
      del self._clients_by_addr[addr]
    ev = event.Event(kb_common.KB_EVENT.CLIENT_DISCONNECTED,
        client_name=name)
    self._kb_env.GetEventHub().PublishEvent(ev)

  def HandleMessage(self, message, channel):
    """Process an incoming client message"""

    # Special case: if this is a new client registering, then proceed without
    # looking up the client.
    if isinstance(message, kegnet_pb2.ClientConnect):
      return self._HandleRegisterClient(channel, message)

    # Any other message should be from a known client.
    client = self.GetClientFromChannel(channel)
    assert(client is not None)

    # Find and dispatch to response handler for this message type.
    handler = self._handlers.get(message.__class__, self._HandleNotImplemented)
    return handler(client, message)

  ### Individual message handlers

  def _HandleRegisterClient(self, channel, message):
    """ Handles the CLIENT_CONNECT message. """
    msg = kegnet_pb2.StatusReply()
    msg.code = 200

    name = message.client_name
    if name is None or not name.strip():  # TODO: validate in Argument
      msg.code = 401
      msg.description = 'Invalid client name'
    elif name in self._clients_by_name:
      msg.code = 402
      msg.description = 'Client name is already in use'
    elif channel.addr in self._clients_by_addr:
      msg.code = 403
      msg.description = 'Only one client per connection'
    else:
      self._CreateClient(name, channel.addr)

    return msg

  def _HandleUnregisterClient(self, client, message):
    msg = kegnet_pb2.StatusReply()
    msg.code = 200
    msg.description = 'OK'
    self._RemoveClient(client)
    return msg

  def _HandleRegisterFlowDev(self, client, message):
    """ Handles the REGISTER_FLOWDEV message.

    Called when the client wants to register a new flow device.
    """
    return client.RegisterFlowDevice(message.name)

  def _HandleUnregisterFlowDev(self, client, message):
    """ Handles the UNREGISTER_FLOWDEV message.

    Called when the client wants to unregister a flow device.
    """
    client._UnregisterDevice(kb_common.KB_DEVICE_TYPE.DEVICE_TYPE_FLOW_DEV,
        message.name)

  def _HandleFlowUpdate(self, client, message):
    """ Handles the FLOW_UPDATE message. """
    return client.FlowUpdate(message.name, message.count)

  def _HandleFlowEnd(self, client, message):
    """ Handles the FLOW_END message. """
    return client.FlowEnd(message.name)

  def _HandleClientDisconnect(self, client, message):
    self._RemoveClient(client)

  def _HandleNotImplemented(self, client, message):
    return


  ### asyncore.dispatcher methods

  def handle_accept(self):
    try:
      conn, addr = self.accept()
    except socket.error:
      raise
    except TypeError:
      raise # ???
    KegnetServerHandler(conn, self)


if __name__ == '__main__':
  server = KegnetServer(name='kegnet', kb_env = None,
                        addr=kb_common.KEGNET_SERVER_BIND_ADDR,
                        port=kb_common.KEGNET_SERVER_BIND_PORT)

  print "Start asyncore"
  asyncore.loop(timeout=2)
  print "finished loop"
