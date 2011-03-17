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
import cStringIO
import logging
import Queue
import socket
import struct
import sys
import threading
import time

import gflags

from pykeg.core import kbevent
from pykeg.core import kbjson
from pykeg.core import kb_common
from pykeg.core import util

FLAGS = gflags.FLAGS

gflags.DEFINE_string('kb_core_addr', kb_common.KB_CORE_DEFAULT_ADDR,
    'The address of the kb_core host, when connecting as a client. '
    'Specify as "<hostname>:<port>".')

gflags.DEFINE_string('kb_core_bind_addr', kb_common.KB_CORE_DEFAULT_ADDR,
    'Address that the kegnet server should bind to. '
    'Specify as "<hostname>:<port>".')

gflags.DEFINE_string('tap_name', 'kegboard.flow0',
    'Default tap name.')

MESSAGE_TERMINATOR = '\n\n'


class KegnetProtocolHandler(asynchat.async_chat):
  """A general purpose request handler for the Kegnet protocol.

  This async_chat subclass can be used for client and server implementations.
  The handler will call _HandleKegnetMessage on receipt of a complete kegnet
  message.
  """
  def __init__(self, sock=None):
    asynchat.async_chat.__init__(self, sock)
    self.set_terminator(MESSAGE_TERMINATOR)
    self._ibuffer = cStringIO.StringIO()
    self._logger = logging.getLogger('kegnet')
    self._in_notifications = Queue.Queue()
    self._lock = threading.Lock()
    self._quit = False

  def stop(self):
    self._quit = True
    if self.socket:
      self.close()

  ### async_chat methods
  @util.synchronized
  def initiate_send(self):
    return asynchat.async_chat.initiate_send(self)

  def collect_incoming_data(self, data):
    self._ibuffer.write(data)

  def found_terminator(self):
    strbuf = self._ibuffer.getvalue()
    self._ibuffer.seek(0)
    self._ibuffer.truncate()

    if not strbuf:
      self._logger.warning('Received empty message')
      return

    try:
      message_dict = kbjson.loads(strbuf)
    except ValueError:
      self._logger.warning('Received malformed message, dropping.')
      return

    # Distinguish between requests, responses, and notifications, using JSON-RPC
    # v2.0 rules
    # (http://groups.google.com/group/json-rpc/web/json-rpc-1-2-proposal):

    self._logger.debug('Received message: %s' % message_dict)
    self.HandleNotification(message_dict)

  def handle_close(self):
    asynchat.async_chat.handle_close(self)
    #self._server.ChannelClosed(self)

  ### KegnetProtocolHandler methods
  def HandleNotification(self, message_dict):
    self._logger.debug('Received notification: %s' % message_dict)
    message = kbevent.DecodeEvent(message_dict)
    self._in_notifications.put(message)

  def PopNotification(self, timeout=None):
    return self._in_notifications.get(timeout=timeout)

  def push(self, data):
    return asynchat.async_chat.push(self, data)

  def SendMessage(self, msg):
    str_message = msg.ToJson(indent=None)
    self.push(str_message + MESSAGE_TERMINATOR)


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

  def HandleNotification(self, message_dict):
    KegnetProtocolHandler.HandleNotification(self, message_dict)
    event_hub = self._server._kb_env.GetEventHub()
    event_hub.PublishEvent(self.PopNotification())


class KegnetClient(KegnetProtocolHandler):
  RECONNECT_BACKOFF = [5, 5, 10, 10, 20, 20, 60]
  def __init__(self, addr=None):
    if not addr:
      addr = FLAGS.kb_core_addr
    self._addr = util.str_to_addr(addr)
    self._last_reconnect = 0
    self._num_retries = 0
    KegnetProtocolHandler.__init__(self)

  def Reconnect(self, force=False):
    backoff_secs = self._ReconnectTimeout()
    if backoff_secs:
      time.sleep(backoff_secs)
    self._last_reconnect = time.time()

    if self.connected:
      return True

    self._logger.info('Connecting to %s:%s' % self._addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    try:
      sock.connect(self._addr)
      self.set_socket(sock)
      self.onConnected()
      self._num_retries = 0
      return True
    except socket.error:
      self._num_retries += 1
      self._logger.info('Connection failed. Retry in %i seconds.' %
          backoff_secs)
      return False

  def _ReconnectTimeout(self):
    if not self._last_reconnect:
      return 0
    prev_wait = time.time() - self._last_reconnect
    pos = min(self._num_retries, len(self.RECONNECT_BACKOFF) - 1)
    amt = self.RECONNECT_BACKOFF[pos]
    if prev_wait < amt:
      return amt - prev_wait
    return 0

  ### convenience functions
  def SendPing(self):
    message = kbevent.Ping()
    return self.SendMessage(message)

  def SendMeterUpdate(self, tap_name, meter_reading):
    message = kbevent.MeterUpdate()
    message.tap_name = tap_name
    message.reading = meter_reading
    return self.SendMessage(message)

  def SendFlowStart(self, tap_name):
    message = kbevent.FlowRequest()
    message.tap_name = tap_name
    message.request = message.Action.START_FLOW
    return self.SendMessage(message)

  def SendFlowStop(self, tap_name):
    message = kbevent.FlowRequest()
    message.tap_name = tap_name
    message.request = message.Action.STOP_FLOW
    return self.SendMessage(message)

  def SendThermoUpdate(self, sensor_name, sensor_value):
    message = kbevent.ThermoEvent()
    message.sensor_name = sensor_name
    message.sensor_value = sensor_value
    return self.SendMessage(message)

  def SendAuthTokenAdd(self, tap_name, auth_device_name, token_value):
    message = kbevent.TokenAuthEvent()
    message.tap_name = tap_name
    message.auth_device_name = auth_device_name
    message.token_value = token_value
    message.status = message.TokenState.ADDED
    return self.SendMessage(message)

  def SendAuthTokenRemove(self, tap_name, auth_device_name, token_value):
    message = kbevent.TokenAuthEvent()
    message.tap_name = tap_name
    message.auth_device_name = auth_device_name
    message.token_value = token_value
    message.status = message.TokenState.REMOVED
    return self.SendMessage(message)

  def onConnected(self):
    self._logger.info('Connected!')

  def onDisconnected(self):
    self._logger.info('Disconnected!')


class SimpleKegnetClient(KegnetClient):

  def serve_forever(self):
    self.Reconnect()
    while not self._quit:
      if not asyncore.socket_map:
        self.onDisconnected()
        self.Reconnect()
        continue
      asyncore.loop(timeout=0.5, count=1)

  def HandleNotification(self, message_dict):
    self._logger.debug('Received notification: %s' % message_dict)
    event = kbevent.DecodeEvent(message_dict)
    if isinstance(event, kbevent.FlowUpdate):
      self.onFlowUpdate(event)
    elif isinstance(event, kbevent.DrinkCreatedEvent):
      self.onDrinkCreated(event)
    elif isinstance(event, kbevent.CreditAddedEvent):
      self.onCreditAdded(event)
    elif isinstance(event, kbevent.SetRelayOutputEvent):
      self.onSetRelayOutput(event)

  def onFlowUpdate(self, event):
    pass

  def onDrinkCreated(self, event):
    pass

  def onCreditAdded(self, event):
    pass

  def onSetRelayOutput(self, event):
    pass


class KegnetClientThread(util.KegbotThread):
  def __init__(self, name, client):
    util.KegbotThread.__init__(self, name)
    self._client = client

  def run(self):
    self._client.serve_forever()


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
    #self._logger.info('Sending event to %i client(s): %s' %
    #  (len(self._clients), ProtoMessageToShortStr(event)))
    str_message = event.ToJson(indent=None)
    for client in self._clients:
      try:
        client.push(str_message + MESSAGE_TERMINATOR)
      except IndexError:
        self._logger.warning('Exception sending to %s' % client)
        util.LogTraceback(self._logger.warning)

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
