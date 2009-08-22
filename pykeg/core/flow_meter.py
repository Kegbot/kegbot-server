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

class FlowMeter(object):
  """Represents a path of fluid volume."""
  def __init__(self, name, max_delta=0, start_volume=None):
    self._name = name
    self._max_delta = max_delta
    self._last_volume = start_volume
    self._total_volume = 0
    self._last_activity = datetime.datetime.fromtimestamp(0)

  def __str__(self):
    return "[Channel vol=%i]" % (self._total_volume,)

  def SetVolume(self, volume, when=None):
    """Report the instantaneous volume of fluid.

    Clients of this interface should provide a monotonically-increasing,
    "odometer-style" value as the volume parameter.  Internally, the FlowMeter
    instance will compute the difference in volume based on any previously
    reported volume.

    If the volume has not yet been reported, the value is simply saved for the
    next report (without incrementing the volume.)
    """
    volume = long(volume)
    if volume < 0:
      raise ValueError, "SetVolume only accepts positive values"

    last_reading = self._last_volume
    if last_reading is None:
      last_reading = volume

    self._last_volume = volume

    if volume >= last_reading:
      # Normal case: zero or positive delta from last reading.
      delta = volume - last_reading
    else:
      # Possible overflow. Resolution algorithm: assume overflow occured at
      # the next power of two following the last reading. Compute the delta to
      # be the difference between last_reading and that power of two, plus
      # whatever the current reading is.
      #
      # This may assume overflow where non occured; for example, if the meter
      # was suddenly reset. MAX_METER_READING_DELTA should be low enough to
      # mitigate this problem.
      for power_of_two in (2**16, 2**32, 2**64):
        if last_reading < power_of_two:
          break
      delta = power_of_two - last_reading + volume

    if self._max_delta and delta > self._max_delta:
      # TODO: should warn and/or accumulate stats
      return 0

    # If there was actually a change, increment total volume and update activity
    # time.
    if delta > 0:
      self._total_volume += delta
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
  def GetVolume(self):
    return self._total_volume

  def GetLastReading(self):
    return self._last_volume

  def GetName(self):
    return self._name

  def GetLastActivity(self):
    return self._last_activity

  def GetIdleTime(self, now=None):
    if not now:
      now = datetime.datetime.now()
    return now - self._last_activity

