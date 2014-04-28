# Copyright 2014 Bevbot LLC, All Rights Reserved
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

"""Methods for manipulating a time series.

A Kegbot core may report a time series (Drink.tick_time_series) for the meter
events that caused a drink.
"""


def from_string(s):
    """Converts a time series to a list of (int, int) tuples.

    The string should be a sequence of zero or more <time>:<amount> pairs.
    Whitespace delimits each pair; leading and trailing whitespace is ignored.

    ValueError is raised on any malformed input.
    """
    pairs = s.strip().split()
    ret = []
    for pair in pairs:
        time, amount = pair.split(':')
        time = int(time)
        amount = int(amount)
        if time < 0:
            raise ValueError('Time cannot be less than zero: %s' % time)
        ret.append((time, amount))
    return ret


def to_string(pairs):
    """Converts a series of (int, int) tuples to a time series string."""
    return ' '.join('%i:%i' % pair for pair in pairs)
