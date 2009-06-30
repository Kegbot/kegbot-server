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

"""Channel (single path of fluid) management module."""

import datetime
import logging

from pykeg.core import flow_meter


class ChannelManagerError(Exception):
  """ Generic ChannelManager error """

class AlreadyRegisteredError(ChannelManagerError):
  """ Raised when attempting to register an already-registered name """

class UnknownChannelError(ChannelManagerError):
  """ Raised when channel requested does not exist """


class Channel(object):
  def __init__(self, name):
    self._name = name
    self._meter = flow_meter.FlowMeter(name)

  def __str__(self):
    return self._name

  def GetName(self):
    return self._name

  def GetMeter(self):
    return self._meter


class ChannelManager(object):
  """Maintains listing of available fluid paths.

  This manager maintains the set of available beer channels.  Channels have a
  one-to-one correspondence with beer taps.  For example, a kegboard controller
  is capable of reading from two flow sensors; thus, it provides two beer
  channels.
  """

  def __init__(self):
    self._logger = logging.getLogger('channel-manager')
    self._channels = {}

  def _ChannelExists(self, name):
    return name in self._channels

  def _CheckChannelExists(self, name):
    if not self._ChannelExists(name):
      raise UnknownChannelError

  def RegisterChannel(self, name):
    self._logger.info('Registering new channel: %s' % name)
    if self._ChannelExists(name):
      raise AlreadyRegisteredError
    self._channels[name] = Channel(name)

  def UnregisterChannel(self, name):
    self._logger.info('Unregistering channel: %s' % name)
    self._CheckChannelExists(name)
    del self._channels[name]

  def GetChannel(self, name):
    self._CheckChannelExists(name)
    return self._channels[name]

  def UpdateDeviceReading(self, name, value):
    meter = self.GetChannel(name).GetMeter()
    delta = meter.SetVolume(value)
    return delta


class Flow:
  def __init__(self, channel):
    self._channel = channel
    self._start_volume = None
    self._end_volume = None

    self._start_time = datetime.datetime.now()
    self._end_time = None

    self._bound_user = None

    self._last_log_time = None

  def UpdateFromMeter(self):
    current_volume = self._channel.GetMeter().GetVolume()
    last_activity_time = self._channel.GetMeter().GetLastActivity()

    if self._start_volume is None:
      self._start_volume = current_volume
    self._end_volume = current_volume

    if self._start_time is None:
      self._start_time = last_activity_time
    self._end_time = last_activity_time

  def GetVolume(self):
    if self._start_volume is None:
      return 0
    return self._end_volume - self._start_volume

  def GetUser(self):
    return self._bound_user

  def GetStartTime(self):
    return self._start_time

  def GetEndTime(self):
    return self._end_time

  def GetIdleTime(self):
    end_time = self._end_time
    if end_time is None:
      end_time = self._start_time
    return datetime.datetime.now() - end_time

  def GetChannel(self):
    return self._channel


class FlowManager(object):
  """Class reponsible for maintaining and servicing flows.

  The manager is responsible for creating Flow instances and managing their
  lifecycle.  It is one layer above the the ChannelManager, in that it does not
  deal with devices directly.

  Flows can be started in multiple ways:
    - Explicitly, by a call to StartFlow
    - Implicitly, by a call to HandleChannelActivity
  """
  def __init__(self, channel_manager):
    self._channel_manager = channel_manager
    self._flow_map = {}
    self._logger = logging.getLogger("flowmanager")

  def GetActiveFlows(self):
    return self._flow_map.values()

  def _GetFlow(self, channel):
    name = channel.GetName()
    return self._flow_map.get(name)

  def StartFlow(self, channel):
    assert not self._GetFlow(channel), "StartFlow while already active!"
    self._flow_map[channel.GetName()] = Flow(channel)
    self._logger.info("Flow created on channel %s" % (channel,))
    return self._GetFlow(channel)

  def EndFlow(self, channel_name):
    channel = self._channel_manager.GetChannel(channel_name)
    flow = self._GetFlow(channel)
    assert flow is not None, "EndFlow on inactive channel!"
    del self._flow_map[channel.GetName()]
    self._logger.info("Flow ended on channel %s" % (channel,))
    return flow

  def UpdateFlow(self, channel_name, volume):
    try:
      channel = self._channel_manager.GetChannel(channel_name)
    except ChannelManagerError:
      # channel is unknown or not available
      return None, None

    is_new = False

    # Get the flow instance; create a new one if needed
    flow = self._GetFlow(channel)
    if not flow:
      flow = self.StartFlow(channel)
      is_new = True

    delta = self._channel_manager.UpdateDeviceReading(channel.GetName(), volume)
    flow.UpdateFromMeter()

    return flow, is_new
