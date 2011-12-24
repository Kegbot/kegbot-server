# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

"""Methods to generate cached statistics from drinks."""

import copy
import inspect
import itertools
import logging

from pykeg.proto import models_pb2

STAT_MAP = {}

def stat(statname):
  def decorate(f):
    setattr(f, 'statname', statname)
    return f
  return decorate

class StatsBuilder:
  def __init__(self, drink, previous=None):
    self.drink = drink
    self.previous = previous
    self.STAT_MAP = {}
    for name, fn in inspect.getmembers(self, inspect.ismethod):
      if hasattr(fn, 'statname'):
        self.STAT_MAP[fn.statname] = fn

  def _AllDrinks(self):
    return []

  def Build(self):
    self.stats = models_pb2.Stats()
    if not self.drink:
      return self.stats
    self.drinks = self._AllDrinks()
    if self.previous:
      self.stats.MergeFrom(self.previous)
    for statname, fn in self.STAT_MAP.iteritems():
      fn()
    return self.stats


class BaseStatsBuilder(StatsBuilder):
  """Builder which generates a variety of stats from object information."""

  @stat('last_drink_id')
  def LastDrinkId(self):
    self.stats.last_drink_id = str(self.drink.seqn)

  @stat('total_volume_ml')
  def TotalVolume(self):
    if not self.previous:
      self.stats.total_volume_ml = sum(drink.volume_ml for drink in self.drinks)
    else:
      self.stats.total_volume_ml += self.drink.volume_ml

  @stat('total_pours')
  def TotalPours(self):
    if not self.previous:
      self.stats.total_pours = self.drinks.count()
    else:
      self.stats.total_pours += 1

  @stat('average_volume_ml')
  def AverageVolume(self):
    if not self.previous:
      count = self.drinks.count()
      average = 0.0
      if count:
        average = sum(drink.volume_ml for drink in self.drinks) / float(count)
      self.stats.average_volume_ml = average
    else:
      vol = self.previous.total_volume_ml
      count = self.previous.total_pours
      vol += self.drink.volume_ml
      count += 1
      self.stats.average_volume_ml = vol / float(count)

  @stat('greatest_volume_ml')
  def GreatestVolume(self):
    if not self.previous:
      res = 0
      drinks = self.drinks.order_by('-volume_ml')
      if drinks.count():
        res = drinks[0].volume_ml
      self.stats.greatest_volume_ml = res
    else:
      if self.drink.volume_ml > self.previous.greatest_volume_ml:
        self.stats.greatest_volume_ml = self.drink.volume_ml

  @stat('greatest_volume_id')
  def GreatestVolumeId(self):
    if not self.previous:
      res = 0
      drinks = self.drinks.order_by('-volume_ml')
      if drinks.count():
        res = drinks[0].seqn
      self.stats.greatest_volume_id = str(res)
    else:
      if self.drink.volume_ml > self.previous.greatest_volume_ml:
        self.stats.greatest_volume_id = str(self.drink.seqn)

  @stat('volume_by_day_of_week')
  def VolumeByDayOfweek(self):
    result = self.stats.volume_by_day_of_week
    if not self.previous:
      # Note: uses the session's starttime, rather than the drink's. This causes
      # late-night sessions to be reported for the day on which they were
      # started.
      volmap = {}
      for drink in self.drinks:
        weekday = drink.session.starttime.strftime('%w')
        if weekday not in volmap:
          volmap[weekday] = 0.0
        volmap[weekday] += drink.volume_ml
      for weekday, volume_ml in volmap.iteritems():
        if volume_ml:
          day = result.add()
          day.weekday = weekday
          day.volume_ml = volume_ml
    else:
      drink_weekday = self.drink.session.starttime.strftime('%w')
      for message in self.stats.volume_by_day_of_week:
        if message.weekday == drink_weekday:
          message.volume_ml += self.drink.volume_ml
          return
      message = result.add()
      message.weekday = drink_weekday
      message.volume_ml = self.drink.volume_ml

  @stat('registered_drinkers')
  def RegisteredDrinkers(self):
    if not self.previous:
      drinkers = set()
      for drink in self.drinks:
        if drink.user:
          drinkers.add(str(drink.user.username))
      self.stats.registered_drinkers.extend(drinkers)
    else:
      if self.drink.user:
        result = self.stats.registered_drinkers
        username = str(self.drink.user.username)
        if username not in result:
          result.append(username)

  @stat('sessions_count')
  def SessionsCount(self):
    if not self.previous:
      all_sessions = set()
      for drink in self.drinks:
        all_sessions.add(str(drink.session.seqn))
      self.stats.sessions_count = len(all_sessions)
    else:
      first_drink = self.drink.session.drinks.order_by('seqn')[0]
      if self.drink.seqn == first_drink.seqn:
        self.stats.sessions_count += 1

  @stat('volume_by_year')
  def VolumeByYear(self):
    if not self.previous:
      volmap = {}
      for drink in self.drinks:
        year = drink.starttime.year
        volmap[year] = volmap.get(year, 0) + drink.volume_ml
      for year, volume_ml in volmap.iteritems():
        rec = self.stats.volume_by_year.add()
        rec.year = year
        rec.volume_ml = volume_ml
    else:
      year = self.drink.starttime.year
      for entry in self.stats.volume_by_year:
        if entry.year == year:
          entry.volume_ml += self.drink.volume_ml
          return
      rec = self.stats.volume_by_year.add()
      rec.year = year
      rec.volume_ml = self.drink.volume_ml

  @stat('has_guest_pour')
  def HasGuestPour(self):
    if not self.previous:
      for drink in self.drinks:
        if not drink.user:
          self.stats.has_guest_pour = True
          return
      self.stats.has_guest_pour = False
    else:
      if not self.stats.has_guest_pour:
        if not self.drink.user:
          self.stats.has_guest_pour = True

  @stat('volume_by_drinker')
  def VolumeByDrinker(self):
    if not self.previous:
      result = self.stats.volume_by_drinker
      volmap = {}
      for drink in self.drinks:
        if drink.user:
          u = drink.user.username
        else:
          u = ''
        volmap[u] = volmap.get(u, 0) + drink.volume_ml
      for username, volume_ml in volmap.iteritems():
        if volume_ml:
          record = result.add()
          record.username = username
          record.volume_ml = volume_ml
    else:
      result = self.stats.volume_by_drinker
      if self.drink.user:
        u = self.drink.user.username
      else:
        u = ''
      for message in result:
        if message.username == u:
          message.volume_ml += self.drink.volume_ml
          return
      message = result.add()
      message.username = u
      message.volume_ml = self.drink.volume_ml

class SystemStatsBuilder(BaseStatsBuilder):
  """Builder of systemwide stats by drink."""
  REVISION = 5

  def _AllDrinks(self):
    qs = self.drink.site.drinks.valid().filter(seqn__lte=self.drink.seqn)
    qs = qs.order_by('seqn')
    return qs


class DrinkerStatsBuilder(SystemStatsBuilder):
  """Builder of user-specific stats by drink."""
  REVISION = 5

  def _AllDrinks(self):
    qs = SystemStatsBuilder._AllDrinks(self)
    qs = qs.filter(user=self.drink.user)
    return qs


class KegStatsBuilder(SystemStatsBuilder):
  """Builder of keg-specific stats."""
  REVISION = 5

  def _AllDrinks(self):
    qs = SystemStatsBuilder._AllDrinks(self)
    qs = qs.filter(keg=self.drink.keg)
    return qs


class SessionStatsBuilder(SystemStatsBuilder):
  """Builder of user-specific stats by drink."""
  REVISION = 5

  def _AllDrinks(self):
    qs = SystemStatsBuilder._AllDrinks(self)
    qs = qs.filter(session=self.drink.session)
    return qs


def main():
  from pykeg.core import models
  last_drink = models.Drink.objects.valid().order_by('-seqn')[0]
  builder = KegStatsBuilder(last_drink)

  print "building..."
  stats = builder.Build()
  print "done"
  print stats

  if False:
    for user in models.User.objects.all():
      last_drink = user.drinks.valid().order_by('-starttime')
      if not last_drink:
        continue
      last_drink = last_drink[0]
      builder = DrinkerStatsBuilder()
      stats = builder.Build(last_drink)
      print '-'*72
      print 'stats for %s' % user
      for k, v in stats.iteritems():
        print '   %s: %s' % (k, v)
      print ''

if __name__ == '__main__':
  import cProfile
  command = """main()"""
  cProfile.runctx( command, globals(), locals(), filename="stats.profile" )

