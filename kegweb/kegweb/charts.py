#!/usr/bin/env python
#
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

"""Chart functions for use by the views module."""

# This module requires pygooglechart. If pygooglechart is unavailable, all
# functions that can return a chart will instead return None.
try:
  import pygooglechart
  USE_GOOGLE_CHARTS = True
except ImportError:
  USE_GOOGLE_CHARTS = False

def volume_chart(vol_by_user):
  """Returns a PieChart2D representing per-user shares.

  Args
    vol_by_user - tuple of (volume in ounces, User)
  Returns
    PieChart2D, or None
  """
  if not USE_GOOGLE_CHARTS:
    return None
  chart = pygooglechart.PieChart2D(300, 150)
  chart.add_data([x[0] for x in vol_by_user])
  chart.set_pie_labels(["%s (%i oz)" % (x[1].username, x[0]) for x in vol_by_user])
  return chart

