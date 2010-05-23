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
  chart = pygooglechart.PieChart2D(300, 125)
  data = []
  labels = []

  for amount, user in vol_by_user[:10]:
    ounces = amount.ConvertTo.Ounce
    data.append(ounces)
    labels.append("%s (%i oz)" % (user.username, ounces))

  other_vol = 0
  for amount, user in vol_by_user[10:]:
    ounces = amount.ConvertTo.Ounce
    other_vol += ounces
  if other_vol:
    data.append(other_vol)
    labels.append("all others (%i oz)" % other_vol)

  chart.add_data(data)
  chart.set_pie_labels(labels)
  return chart

