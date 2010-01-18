# Copyright 2008-2010 Mike Wakerly <opensource@hoho.com>
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

# TODO(mikey): need to isolate internal-only events (like QuitEvent) from
# external ones (like FlowUpdate).
# TODO(mikey): add onDisconnect handler and retry/backoff
# TODO(mikey): also raise an exception on socket errors

import asyncore
import asynchat
import socket
import cStringIO
import logging
import Queue
import simplejson
import struct
import threading
import time

from pykeg.core import kb_common
from pykeg.core import util
from pykeg.core.net import kegnet_pb2
from pykeg.external.gflags import gflags
from google.protobuf import message as protobuf_message

FLAGS = gflags.FLAGS

gflags.DEFINE_string('kb_core_addr', kb_common.KB_CORE_DEFAULT_ADDR,
    'The address of the kb_core host, when connecting as a client. '
    'Specify as "<hostname>:<port>".')

gflags.DEFINE_string('kb_core_bind_addr', kb_common.KB_CORE_DEFAULT_ADDR,
    'Address that the kegnet server should bind to. '
    'Specify as "<hostname>:<port>".')

gflags.DEFINE_string('tap_name', 'kegboard.flow0',
    'Default tap name.')


def ProtoMessageToDict(message):
  ret = {}
  if not message.IsInitialized():
    raise ValueError, message
  for descriptor, value in message.ListFields():
    if descriptor.type == descriptor.TYPE_MESSAGE:
      ret[descriptor.name] = ToDict(value)
    else:
      ret[descriptor.name] = value
  return ret

def DictToProtoMessage(values, out_message):
  for name, field in out_message.DESCRIPTOR.fields_by_name.iteritems():
    if name not in values:
      if field.label == field.LABEL_REQUIRED:
        raise ValueError, "Missing required field %s" % name
      continue

    value = values.get(name)
    if field.type == field.TYPE_MESSAGE:
      inner_message = gettattr(out_message, name)
      value = FromDict(inner_message, value)
    setattr(out_message, name, value)
  return out_message

def ProtoMessageToJson(message):
  wrapper = {
    'method': message.DESCRIPTOR.name,
    'id': None,
    'params': ProtoMessageToDict(message),
  }
  return simplejson.dumps(wrapper)

NAME_TO_MESSAGE_CLASS = {}
for cls in protobuf_message.Message.__subclasses__():
  NAME_TO_MESSAGE_CLASS[cls.DESCRIPTOR.name] = cls

def JsonToProtoMessage(strmessage):
  message = simplejson.loads(strmessage)
  message_name = message['method']
  message_class = NAME_TO_MESSAGE_CLASS[message_name]
  return DictToProtoMessage(message['params'], message_class())

def ProtoMessageToShortStr(message):
  name = message.DESCRIPTOR.name
  values = str(message).replace('\n', ' ')
  # TODO(mikey): show submessages properly
  return '<%s: %s>' % (name, values)

class KegnetProtocolHandler(asynchat.async_chat):
  """A general purpose request handler for the Kegnet protocol.

  This async_chat subclass can be used for client and server implementations.
  The handler will call _HandleKegnetMessage on receipt of a complete kegnet
  message.
  """
  def __init__(self, sock=None, map=None):
    asynchat.async_chat.__init__(self, sock, map)
    self.set_terminator('\n\n')
    self._ibuffer = cStringIO.StringIO()
    self._logger = logging.getLogger('kegnet')

  ### async_chat methods
  def collect_incoming_data(self, data):
    self._ibuffer.write(data)

  def found_terminator(self):
    strbuf = self._ibuffer.getvalue()
    self._ibuffer.seek(0)
    self._ibuffer.truncate()

    if not strbuf:
      self._logger.warning('Received empty message')
    else:
      message = JsonToProtoMessage(strbuf)
      self._logger.info('<- %s' % ProtoMessageToShortStr(message))
      self.HandleNotification(message)

  def handle_close(self):
    asynchat.async_chat.handle_close(self)
    #self._server.ChannelClosed(self)

  ### KegnetProtocolHandler methods
  def HandleNotification(self, message):
    pass

  def HandleRequest(self, message):
    pass

  def HandleResponse(self, message):
    pass

  def SendMessage(self, msg):
    str_message = ProtoMessageToJson(msg)
    self._logger.info('-> %s' % str_message)
    self.push(str_message)
    self.push('\n\n')


class KegnetServerHandler(KegnetProtocolHandler):
  """ An asyncore handler for the core kegnet server. """
  def __init__(self, sock, server):
    KegnetProtocolHandler.__init__(self, sock)
    self._server = server
    self._server.ChannelOpened(self)

  def handle_close(self):
    KegnetProtocolHandler.handle_close(self)
    self._logger.info('Closing down...')
    self._server.ChannelClosed(self)

  def _HandleBadMessage(self, strdata, exception):
    self._server._logger.warn("Unknown command from %s, closing connection" %
                              str(self.addr))
    self._server._logger.warn("Exception was: %s" % str(exception))
    self._server.ChannelClosed(self)
    self.close()

  def HandleNotification(self, message):
    event_hub = self._server._kb_env.GetEventHub()
    event_hub.PublishEvent(message)


class KegnetClient(KegnetProtocolHandler):
  def __init__(self, addr=FLAGS.kb_core_addr, map=None):
    self._in_notifications = Queue.Queue()
    while True:
      try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.connect(util.str_to_addr(addr))
        break
      except socket.error:
        # TODO(mikey): quick hack. need much better retry hooks (logging,
        # onDisconnect/onReconnect callbacks)
        time.sleep(2)
    KegnetProtocolHandler.__init__(self, sock, map)

  def HandleNotification(self, message):
    self._logger.info('<- %s' % message)
    self._in_notifications.put(message)

  def PopNotification(self, timeout=None):
    return self._in_notifications.get(timeout=timeout)

  ### convenience functions
  def SendPing(self):
    message = kegnet_pb2.Ping()
    return self.SendMessage(message)

  def SendMeterUpdate(self, tap_name, meter_reading):
    message = kegnet_pb2.MeterUpdate()
    message.tap_name = tap_name
    message.reading = meter_reading
    return self.SendMessage(message)

  def SendFlowStart(self, tap_name):
    message = kegnet_pb2.FlowRequest()
    message.tap_name = tap_name
    message.request = message.START_FLOW
    return self.SendMessage(message)

  def SendFlowStop(self, tap_name):
    message = kegnet_pb2.FlowRequest()
    message.tap_name = tap_name
    message.request = message.STOP_FLOW
    return self.SendMessage(message)

  def SendThermoUpdate(self, sensor_name, sensor_value):
    message = kegnet_pb2.ThermoEvent()
    message.sensor_name = sensor_name
    message.sensor_value = sensor_value
    return self.SendMessage(message)

  def SendAuthTokenAdd(self, tap_name, auth_device_name, token_value):
    message = kegnet_pb2.TokenAuthEvent()
    message.tap_name = tap_name
    message.auth_device_name = auth_device_name
    message.token_value = token_value
    message.status = message.ADDED
    return self.SendMessage(message)

  def SendAuthTokenRemove(self, tap_name, auth_device_name, token_value):
    message = kegnet_pb2.TokenAuthEvent()
    message.tap_name = tap_name
    message.auth_device_name = auth_device_name
    message.token_value = token_value
    message.status = message.REMOVED
    return self.SendMessage(message)


class KegnetServer(asyncore.dispatcher):
  """asyncore server implementation for Kegnet protocol"""
  def __init__(self, name, kb_env, addr='', port=0, qsize=5):
    self._name = name
    self._kb_env = kb_env
    self._logger = logging.getLogger(self._name)
    self._bind_address = util.str_to_addr(addr)
    self._qsize = qsize
    self._clients = set()
    self._lock = threading.Lock()
    asyncore.dispatcher.__init__(self)

  def StartServer(self):
    self._logger.info("Starting server on %s" % str(self._bind_address,))
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.set_reuse_addr()
    self.bind(self._bind_address)
    self.listen(self._qsize)

  def StopServer(self):
    self._logger.info("Stopping server")
    self.close()

  @util.synchronized
  def ChannelOpened(self, channel):
    self._logger.info('Remote host connected: %s:%i' % channel.addr)
    self._clients.add(channel)

  @util.synchronized
  def ChannelClosed(self, channel):
    self._logger.info('Remote host closed: %s:%i' % channel.addr)
    self._clients.remove(channel)

  @util.synchronized
  def SendEventToClients(self, event):
    # TODO(mikey): filter events -- should be based on subscriptions & exclude
    # internal events.
    if not self._clients:
      return
    self._logger.info('Sending event to %i client(s): %s' %
      (len(self._clients), ProtoMessageToShortStr(event)))
    str_message = ProtoMessageToJson(event)
    for client in self._clients:
      try:
        client.push(str_message)
        client.push('\n\n')
      except IndexError:
        self._logger.warning('Exception sending to %s' % client)

  ### asyncore.dispatcher methods

  def handle_accept(self):
    # TODO(mikey): error handling
    conn, addr = self.accept()
    conn.settimeout(1)
    KegnetServerHandler(conn, self)


if __name__ == '__main__':
  server = KegnetServer(name='kegnet', kb_env=None,
      addr=FLAGS.kb_core_bind_addr)

  print "Start asyncore"
  asyncore.loop(timeout=2)
  print "finished loop"
