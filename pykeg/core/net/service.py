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

"""RPC service implementations."""

import logging

from pykeg.core import event
from pykeg.core import kb_common
from pykeg.core import manager
from pykeg.core.net.proto import kegnet_pb2
from pykeg.core.net.proto import rpc_pb2

REPLY_OK = kegnet_pb2.StatusReply()
REPLY_OK.code = kegnet_pb2.StatusReply.OK

class CoreService(kegnet_pb2.Core):
  def __init__(self, name, kb_env):
    self._name = name
    self._kb_env = kb_env
    self._logger = logging.getLogger(self._name)

    self._clients_by_name = {}

  ### Service methods

  def Login(self, rpc_controller, request, done):
    client = self._CreateClient(request.client_name)
    done(request)

  def Logout(self, rpc_controller, request, done):
    self._RemoveClient(self._GetClient(request.client_name))
    done(REPLY_OK)

  def PostMeterReading(self, rpc_controller, request, done):
    client = self._GetClientFromHandle(request.handle)
    client.RegisterFlowDevice(request.name)
    client.FlowUpdate(request.name, request.value)
    done(REPLY_OK)

  def PostOutputStatus(self, rpc_controller, request, done):
    pass

  def PostThermalReading(self, rpc_controller, request, done):
    pass

  def StartFlow(self, rpc_controller, request, done):
    client = self._GetClientFromHandle(request.handle)
    done(REPLY_OK)

  def StopFlow(self, rpc_controller, request, done):
    client = self._GetClientFromHandle(request.handle)
    client.FlowEnd(request.channel_info.name)
    done(REPLY_OK)

  ### Internal methods

  def _GetClientFromHandle(self, client_handle):
    return self._clients_by_name.get(client_handle.client_name)

  def _CreateClient(self, client_name):
    """ Creates a new client.

    A client is associated with a connection to the server. If the channel dies,
    the client is removed and all devices registered to the client should be
    removed as well.
    """
    self._logger.info('Creating new client "%s"' % client_name)
    client = KegnetClientState(client_name, self._kb_env)
    self._clients_by_name[client_name] = client
    ev = event.Event(kb_common.KB_EVENT.CLIENT_CONNECTED,
        client_name=client_name)
    self._kb_env.GetEventHub().PublishEvent(ev)
    return client

  def _RemoveClient(self, client):
    self._logger.info('Deleting client: %s' % client)
    name = client._client_name
    client.Cleanup()
    if name in self._clients_by_name:
      del self._clients_by_name[name]
    ev = event.Event(kb_common.KB_EVENT.CLIENT_DISCONNECTED,
        client_name=name)
    self._kb_env.GetEventHub().PublishEvent(ev)


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
  def __init__(self, client_name, kb_env):
    self._client_name = client_name
    self._devices = {
      'flow' : {},
      'relay' : {},
    }
    self._logger = logging.getLogger(':'.join(('kegnet', self._client_name)))
    self._kb_env = kb_env

  def __str__(self):
    return "[%s]" % (self._client_name,)

  def GetName(self):
    return self._client_name

  def _GetDevice(self, device_type, local_name):
    return self._devices.get(device_type, {}).get(local_name)

  def _GetFlowDevice(self, local_name):
    return self._GetDevice('flow', local_name)

  def _RegisterDevice(self, device):
    if isinstance(device, KegnetFlowDevice):
      channel_manager = self._kb_env.GetChannelManager()
      try:
        channel_manager.RegisterChannel(device.GetGlobalName())
      except manager.AlreadyRegisteredError:
        return False
      self._devices[device.GetType()][device.GetLocalName()] = device
      return True

    return False

  def Cleanup(self):
    channel_manager = self._kb_env.GetChannelManager()
    for name, device in self._devices['flow'].iteritems():
      self._logger.info('Removing device: %s' % name)
      channel_manager.UnregisterDevice(device.GetGlobalName())

  def RegisterFlowDevice(self, name):
    device = self._GetFlowDevice(name)
    if not device:
      self._logger.info('Registering new flow device: %s' % (name,))
      flowdev = KegnetFlowDevice(self, name)
      device = self._RegisterDevice(flowdev)
    return device

  def FlowUpdate(self, name, meter_reading):
    flow_manager = self._kb_env.GetFlowManager()
    self._logger.debug('Flow update: %s %s' % (name, meter_reading))
    device = self._GetFlowDevice(name)

    ev = event.Event(kb_common.KB_EVENT.FLOW_DEV_ACTIVITY)
    ev.device_name = device.GetGlobalName()
    ev.meter_reading = meter_reading
    self._logger.debug('Publishing event: %s' % ev)
    self._kb_env.GetEventHub().PublishEvent(ev)

  def FlowStart(self, name):
    self.RegisterFlowDevice(name)
    flow_manager = self._kb_env.GetFlowManager()
    device = self._GetFlowDevice(name)
    ev = event.Event(kb_common.KB_EVENT.FLOW_START,
        device_name=device.GetGlobalName())
    self._kb_env.GetEventHub().PublishEvent(ev)

  def FlowEnd(self, name):
    flow_manager = self._kb_env.GetFlowManager()
    device = self._GetFlowDevice(name)
    ev = event.Event(kb_common.KB_EVENT.END_FLOW,
        device_name=device.GetGlobalName())
    self._kb_env.GetEventHub().PublishEvent(ev)

