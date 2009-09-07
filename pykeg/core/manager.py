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

"""Tap (single path of fluid) management module."""

import datetime
import logging

from pykeg.core import models
from pykeg.core import flow_meter


class TapManagerError(Exception):
  """ Generic TapManager error """

class AlreadyRegisteredError(TapManagerError):
  """ Raised when attempting to register an already-registered name """

class UnknownTapError(TapManagerError):
  """ Raised when tap requested does not exist """


class Tap(object):
  def __init__(self, name):
    self._name = name
    self._meter = flow_meter.FlowMeter(name)

  def __str__(self):
    return self._name

  def GetName(self):
    return self._name

  def GetMeter(self):
    return self._meter


class TapManager(object):
  """Maintains listing of available fluid paths.

  This manager maintains the set of available beer taps.  Taps have a
  one-to-one correspondence with beer taps.  For example, a kegboard controller
  is capable of reading from two flow sensors; thus, it provides two beer
  taps.
  """

  def __init__(self):
    self._logger = logging.getLogger('tap-manager')
    self._taps = {}
    all_taps = models.KegTap.objects.all()
    for tap in all_taps:
      self.RegisterTap(tap.meter_name)

  def TapExists(self, name):
    return name in self._taps

  def _CheckTapExists(self, name):
    if not self.TapExists(name):
      raise UnknownTapError

  def RegisterTap(self, name):
    self._logger.info('Registering new tap: %s' % name)
    if self.TapExists(name):
      raise AlreadyRegisteredError
    self._taps[name] = Tap(name)

  def UnregisterTap(self, name):
    self._logger.info('Unregistering tap: %s' % name)
    self._CheckTapExists(name)
    del self._taps[name]

  def GetTap(self, name):
    self._CheckTapExists(name)
    return self._taps[name]

  def UpdateDeviceReading(self, name, value):
    meter = self.GetTap(name).GetMeter()
    delta = meter.SetVolume(value)
    return delta


class Flow:
  def __init__(self, tap):
    self._tap = tap
    self._start_volume = None
    self._end_volume = None

    self._start_time = datetime.datetime.now()
    self._end_time = None

    self._bound_user = None

    self._last_log_time = None

  def UpdateFromMeter(self):
    current_volume = self._tap.GetMeter().GetVolume()
    last_activity_time = self._tap.GetMeter().GetLastActivity()

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

  def SetUser(self, user):
    self._bound_user = user

  def GetStartTime(self):
    return self._start_time

  def GetEndTime(self):
    return self._end_time

  def GetIdleTime(self):
    end_time = self._end_time
    if end_time is None:
      end_time = self._start_time
    return datetime.datetime.now() - end_time

  def GetTap(self):
    return self._tap


class FlowManager(object):
  """Class reponsible for maintaining and servicing flows.

  The manager is responsible for creating Flow instances and managing their
  lifecycle.  It is one layer above the the TapManager, in that it does not
  deal with devices directly.

  Flows can be started in multiple ways:
    - Explicitly, by a call to StartFlow
    - Implicitly, by a call to HandleTapActivity
  """
  def __init__(self, tap_manager):
    self._tap_manager = tap_manager
    self._flow_map = {}
    self._logger = logging.getLogger("flowmanager")

  def GetActiveFlows(self):
    return self._flow_map.values()

  def GetFlow(self, tap_name):
    return self._flow_map.get(tap_name)

  def StartFlow(self, tap_name):
    if not self.GetFlow(tap_name):
      tap = self._tap_manager.GetTap(tap_name)
      self._flow_map[tap_name] = Flow(tap)
      self._logger.info('StartFlow: Flow created on %s' % (tap_name,))
    else:
      self._logger.info('StartFlow: Flow already exists on %s' % tap_name)
    return self.GetFlow(tap_name)

  def EndFlow(self, tap_name):
    flow = self.GetFlow(tap_name)
    if flow:
      tap = flow.GetTap()
      del self._flow_map[tap_name]
      self._logger.info('EndFlow: Flow ended on tap %s' % (tap_name,))
    else:
      self._logger.info('EndFlow: No existing flow on tap %s' % (tap_name,))
    return flow

  def UpdateFlow(self, tap_name, volume):
    try:
      tap = self._tap_manager.GetTap(tap_name)
    except TapManagerError:
      # tap is unknown or not available
      return None, None

    is_new = False

    # Get the flow instance; create a new one if needed
    delta = self._tap_manager.UpdateDeviceReading(tap.GetName(), volume)
    flow = self.GetFlow(tap_name)
    if not flow and delta:
      flow = self.StartFlow(tap_name)
      is_new = True

    if flow:
      flow.UpdateFromMeter()

    return flow, is_new


class AuthenticationManager(object):
  def _GetUserAtTap(self, tap):
    """Returns the currently authorized user at the tap."""

  def _TapIdle(self, tap):
    """Called when the given tap has become idle."""
