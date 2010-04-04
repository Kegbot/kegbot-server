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

"""Utility functions for use by the views module."""

from pykeg.core import models
from pykeg.core import units

def all_valid_drinks():
  drinks = models.Drink.objects.filter(status='valid')
  drinks = drinks.filter(volume_ml__gt=0)
  return drinks

def current_keg():
  q = models.Keg.objects.filter(status='online').order_by('-id')
  if len(q):
    return q[0]

def user_is_hidden(user):
  try:
    profile = user.get_profile()
  except models.UserProfile.DoesNotExist:
    return False

  return profile.HasLabel('__hidden__')

def keg_drinks(keg):
  if not keg:
    return []
  return models.Drink.objects.filter(status='valid', keg=keg, volume_ml__gt=0)

def keg_drinkers_by_volume(keg):
  return drinkers_by_volume(keg_drinks(keg))

def drinkers_by_volume(drinks):
  ret = {}
  for d in drinks:
    ret[d.user] = ret.get(d.user, units.Quantity(0, units.RECORD_UNIT)) + d.Volume()
  outlist = []
  for user, totalvol in ret.iteritems():
    if user_is_hidden(user):
      continue
    outlist.append((totalvol, user))
  outlist.sort(reverse=True)
  return outlist

def drinkers_by_cost(drinks):
  cost_map = {}
  for d in drinks:
    keg_volume = d.keg.size.Volume()
    keg_cost = d.keg.origcost
    drink_pct_keg = d.Volume() / keg_volume
    drink_cost = keg_cost * drink_pct_keg
    cost_map[d.user] = cost_map.get(d.user, 0.0) + drink_cost
  ret = [(v, k) for (k, v) in cost_map.iteritems()]
  ret.sort(reverse=True)
  return ret
