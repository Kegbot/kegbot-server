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

def stat(name, default=None):
  def decorate(f):
    setattr(f, 'statname', name)
    setattr(f, 'statdefault', default)
    return f
  return decorate

class StatsBuilder:
  def __init__(self, drink, previous=None):
    self._drink = drink
    self._logger = logging.getLogger('stats-builder')

    if previous is None:
      previous = {}

    prev_seqn = previous.get('_seqn', -1)
    prev_revision = previous.get('_revision', -1)

    if (prev_seqn == drink.seqn) and not Force:
      # Skip if asked to regenerate same stats.
      self._logger.debug('skipping: same seqn')
      return
    elif prev_seqn != (drink.seqn - 1):
      # Invalidate previous stats if not recomputing against the next seqn.
      self._logger.debug('invalidating: not sequential')
      previous = {}
    elif prev_revision != self.REVISION:
      # Invalidate previous stats if builder revisions have changed.
      self._logger.debug('invalidating: older revision')
      previous = {}

    self._previous = previous

  def _AllDrinks(self):
    raise NotImplementedError

  def _AllStats(self):
    for name, cls in inspect.getmembers(self, inspect.isclass):
      if hasattr(cls, 'statname'):
        yield (cls.statname, cls.statdefault, cls)

  def Build(self):
    drinks = self._AllDrinks()
    result = copy.deepcopy(self._previous)
    for statname, statdefault, cls in self._AllStats():
      o = cls()
      if statname not in result:
        self._logger.debug('+++ %s (FULL)' % statname)
        result[statname] = o.Full(drinks)
      else:
        self._logger.debug('+++ %s (partial)' % statname)
        result[statname] = o.Incremental(self._drink, result[statname])

    result['_revision'] = self.REVISION
    result['_seqn'] = self._drink.seqn
    return result


class Stat:
  def __init__(self):
    pass
  def Full(self, drinks):
    raise NotImplementedError
  def Incremental(self, drink, previous):
    raise NotImplementedError


class BaseStatsBuilder(StatsBuilder):
  """Builder which generates a variety of stats from object information."""

  @stat('total_volume', default=0)
  class TotalVolume(Stat):
    def Full(self, drinks):
      return sum(drink.volume_ml for drink in drinks)
    def Incremental(self, drink, previous):
      return previous + drink.volume_ml

  @stat('total_count', default=0)
  class TotalPours(Stat):
    def Full(self, drinks):
      return drinks.count()
    def Incremental(self, drink, previous):
      return previous + 1

  @stat('volume_avg')
  class AverageVolume(Stat):
    def Full(self, drinks):
      count = drinks.count()
      if count:
        average = sum(drink.volume_ml for drink in drinks) / float(count)
      else:
        average = 0
      return {'count': count, 'average': average}
    def Incremental(self, drink, previous):
      average = previous['average']
      count = previous['count']
      vol = drink.volume_ml

      res = previous
      res['average'] = (average*count + vol) / (count + 1)
      res['count'] = count + 1
      return res

  @stat('volume_max')
  class LargestVolume(Stat):
    def Full(self, drinks):
      res = {'volume': 0, 'id': 0}
      drinks = drinks.order_by('-volume_ml')
      if drinks.count():
        res['volume'] = drinks[0].volume_ml
        res['id'] = drinks[0].seqn
      return res
    def Incremental(self, drink, previous):
      if drink.volume_ml <= previous['volume']:
        return previous
      previous['volume'] = drink.volume_ml
      previous['id'] = drink.seqn
      return previous

  @stat('volume_min')
  class SmallestVolume(Stat):
    def Full(self, drinks):
      res = {'volume': 0, 'id': 0}
      drinks = drinks.order_by('volume_ml')
      if drinks.count():
        res['volume'] = drinks[0].volume_ml
        res['id'] = drinks[0].seqn
      return res
    def Incremental(self, drink, previous):
      if drink.volume_ml >= previous['volume']:
        return previous
      previous['volume'] = drink.volume_ml
      previous['id'] = drink.seqn
      return previous

  @stat('volume_by_day_of_week')
  class VolumeByDayOfweek(Stat):
    def Full(self, drinks):
      # Note: uses the session's starttime, rather than the drink's. This causes
      # late-night sessions to be reported for the day on which they were
      # started.
      volmap = dict((str(i), 0) for i in xrange(7))
      for drink in drinks:
        weekday = str(drink.session.starttime.weekday())
        volmap[weekday] += drink.volume_ml
      return volmap
    def Incremental(self, drink, previous):
      weekday = str(drink.session.starttime.weekday())
      previous[weekday] += drink.volume_ml
      return previous

  @stat('volume_by_drinker')
  class VolumeByDrinker(Stat):
    def Full(self, drinks):
      volmap = {}
      for drink in drinks:
        if drink.user:
          u = drink.user.username
        else:
          u = None
        volmap[u] = volmap.get(u, 0) + drink.volume_ml
      return volmap
    def Incremental(self, drink, previous):
      if drink.user:
        u = drink.user.username
      else:
        u = None
      previous[u] = previous.get(u, 0) + drink.volume_ml
      return previous

  @stat('drinkers')
  class Drinkers(Stat):
    def Full(self, drinks):
      drinkers = set()
      for drink in drinks:
        u = None
        if drink.user:
          u = drink.user.username
        if u not in drinkers:
          drinkers.add(u)
      return list(drinkers)
    def Incremental(self, drink, previous):
      u = None
      if drink.user:
        u = drink.user.username
      if u not in previous:
        previous.append(u)
      return previous

  @stat('registered_drinkers')
  class RegisteredDrinkers(Stat):
    def Full(self, drinks):
      drinkers = set()
      for drink in drinks:
        if drink.user and drink.user.username not in drinkers:
          drinkers.add(drink.user.username)
      return list(drinkers)
    def Incremental(self, drink, previous):
      if drink.user and drink.user.username not in previous:
        previous.append(drink.user.username)
      return previous


class SystemStatsBuilder(BaseStatsBuilder):
  """Builder of systemwide stats by drink."""
  REVISION = 5

  def _AllDrinks(self):
    qs = self._drink.site.drinks.valid().filter(seqn__lt=self._drink.seqn)
    qs = qs.order_by('seqn')
    return qs


class DrinkerStatsBuilder(SystemStatsBuilder):
  """Builder of user-specific stats by drink."""
  REVISION = 5

  def _AllDrinks(self):
    qs = SystemStatsBuilder._AllDrinks(self)
    qs = qs.filter(user=self._drink.user)
    return qs


class KegStatsBuilder(SystemStatsBuilder):
  """Builder of keg-specific stats."""
  REVISION = 5

  def _AllDrinks(self):
    qs = SystemStatsBuilder._AllDrinks(self)
    qs = qs.filter(keg=self._drink.keg)
    return qs


class SessionStatsBuilder(SystemStatsBuilder):
  """Builder of user-specific stats by drink."""
  REVISION = 5

  def _AllDrinks(self):
    qs = SystemStatsBuilder._AllDrinks(self)
    qs = qs.filter(session=self._drink.session)
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
      last_drink = user.drinks.all().order_by('-endtime')
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

