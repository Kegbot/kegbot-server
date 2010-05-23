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

"""Classes to generate per-object statistics used by the frontend."""

# TODO(mikey): move this & dependencies to pykeg

from pykeg.web.kegweb import charts
from pykeg.web.kegweb import view_util

from pykeg.core import models
from pykeg.core import units

class UserStats:
  def __init__(self, user):
    self.user = user
    self._InitStats()

  def _InitStats(self):
    drinks = self.AllDrinks()
    volume = units.Quantity(0)
    for d in drinks:
      volume += d.Volume()
    self._total_volume = volume

  def AllDrinks(self):
    drinks = view_util.all_valid_drinks().filter(user=self.user).order_by('-starttime')
    return drinks

  def AllDrinksAsc(self):
    drinks = view_util.all_valid_drinks().filter(user=self.user).order_by('starttime')
    return drinks

  def AllSessions(self):
    sessions = self.user.drinkingsession_set.all()
    sessions = sessions.order_by('-starttime')
    return sessions

  def UserSessions(self):
    return self.user.session_parts.all().order_by('-starttime')

  def EarliestDrink(self):
    drinks = self.AllDrinksAsc()
    if drinks.count():
      return drinks[0]
    else:
      return None

  def HasHadADrink(self):
    return self.EarliestDrink() is not None

  def LatestDrink(self):
    drinks = self.AllDrinks()
    if drinks.count():
      return drinks[0]
    else:
      return None

  def TotalVolume(self):
    return self._total_volume


class KegStats:
  def __init__(self, keg):
    self.keg = keg

  def AllDrinks(self):
    return view_util.keg_drinks(self.keg).order_by('-id')

  def AllDrinkers(self):
    return set(d.user for d in self.AllDrinks())

  def AllDrinkersCount(self):
    return len(self.AllDrinkers())

  def AllUsersByVolume(self):
    return view_util.drinkers_by_volume(self.AllDrinks())

  def TopUsersByVolume(self):
    return self.AllUsersByVolume()[:5]

  def AllUsersByCost(self):
    return view_util.drinkers_by_cost(self.AllDrinks())

  def ChartUsersByVolume(self):
    return charts.volume_chart(self.AllUsersByVolume()).get_url()

  def NextKeg(self):
    next_keg = models.Keg.objects.filter(status='offline')
    next_keg = models.Keg.objects.filter(id__gt=self.keg.id)
    next_keg = next_keg.order_by('id')
    if next_keg.count():
      return next_keg[0]
    else:
      return None

  def Sessions(self):
    return self.keg.drinkingsession_set.all()

  def NumSessions(self):
    return self.keg.drinkingsession_set.count()

  def PercentFull(self):
    return 100.0 * (float(self.keg.remaining_volume()) / float(self.keg.full_volume()))

  def PreviousKeg(self):
    prev_keg = models.Keg.objects.filter(channel=self.keg.channel)
    prev_keg = models.Keg.objects.filter(status='offline')
    prev_keg = models.Keg.objects.filter(id__lt=self.keg.id)
    prev_keg = prev_keg.order_by('-id')
    if prev_keg.count():
      return prev_keg[0]
    else:
      return None

  def VolumePoured(self):
    return self.keg.served_volume()

  def VolumeRemaining(self):
    return self.keg.remaining_volume()

