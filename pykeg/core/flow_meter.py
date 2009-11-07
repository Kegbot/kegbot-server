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

"""Utility module for summing flows."""

import datetime
import logging

class FlowMeter(object):
  """Represents a path of fluid volume."""
  def __init__(self, name, max_delta=0, start_ticks=None):
    self._name = name
    self._max_delta = max_delta
    self._last_ticks = start_ticks
    self._total_ticks = 0
    self._last_activity = datetime.datetime.fromtimestamp(0)
    self._logger = logging.getLogger('flowmeter-%s' % self._name)

  def __str__(self):
    return "<FlowMeter %s ticks=%i>" % (self._name, self.GetTicks())

  def SetTicks(self, ticks, when=None):
    """Report the instantaneous reading of the meter.

    Clients of this interface should provide a monotonically-increasing,
    "odometer-style" value as the ticks parameter.  Internally, the FlowMeter
    instance will compute the difference in ticks based on any previously
    reported ticks.

    If a value for ticks has not yet been reported, the value is simply saved
    for the next report (without incrementing the total ticks.)
    """
    ticks = long(ticks)
    if ticks < 0:
      raise ValueError, "SetTicks only accepts positive values"

    last_reading = self._last_ticks
    if last_reading is None:
      last_reading = ticks

    self._last_ticks = ticks

    if ticks >= last_reading:
      # Normal case: zero or positive delta from last reading.
      delta = ticks - last_reading
    else:
      # Overflow case: ticks < last ticks
      # If the value is less than the max delta, then use it. Some ticks will be
      # lost, since we can't be sure where the overflow occurred. Drop the
      # reading otherwise.
      self._logger.warning('New ticks report less than previous: %i < %i' %
          (ticks, last_reading))
      if ticks < self._max_delta:
        # The value is less than the max delta. In this case, assume the device
        # wrapped around or reset to zero, and use the current reading as the
        # absolute value. Some ticks may be lost.
        # TODO(mikey): should warn and/or accumulate stats
        delta = ticks
      else:
        # The value is greater than the maximum delta; drop the reading, since
        # we cannot safely accept it.
        # TODO(mikey): should warn and/or accumulate stats
        delta = 0

    if self._max_delta and delta > self._max_delta:
      self._logger.warning('Delta greater than maximum, dropping reading. '
          '(%i > %i)' % (delta, self._max_delta))
      # TODO(mikey): accumulate stat somewhere
      # TODO(mikey): add sequence number to updates, or guard against reset by
      # some other means..?
      return 0

    # If there was actually a change, increment total ticks and update activity
    # time.
    if delta > 0:
      self._total_ticks += delta
      self._SetActivity(when)
      return delta

    # No activity
    return 0

  def _SetActivity(self, when=None):
    """Internal method to update the last activity timestamp."""
    if not when:
      when = datetime.datetime.now()
    self._last_activity = when

  ### Accessors
  def GetTicks(self):
    return self._total_ticks

  def GetLastReading(self):
    return self._last_ticks

  def GetName(self):
    return self._name

  def GetLastActivity(self):
    return self._last_activity

  def GetIdleTime(self, now=None):
    if not now:
      now = datetime.datetime.now()
    return now - self._last_activity

