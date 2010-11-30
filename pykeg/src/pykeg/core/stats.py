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

import inspect
import itertools

def stat(name, default=None):
  def decorate(f):
    setattr(f, 'statname', name)
    setattr(f, 'statdefault', default)
    return f
  return decorate

class StatsBuilder(object):

  def __init__(self, prev_stats=None):
    if prev_stats is None:
      prev_stats = {}
    self._prev_stats = prev_stats

  def AllStats(self):
    for name, method in inspect.getmembers(self, inspect.ismethod):
      if hasattr(method, 'statname'):
        yield (method.statname, method.statdefault, method)

  def Build(self, obj, prev_stats=None, prev_objs=None):
    if prev_objs is None:
      prev_objs = self._PrevObjs(obj).order_by('endtime')

    stats = self._prev_stats
    for drink in itertools.chain(prev_objs, [obj]):
      for statname, statdefault, fn in self.AllStats():
        previous_value = stats.get(statname, statdefault)
        stats[statname] = fn(drink, previous_value)
    return stats


class BaseStatsBuilder(StatsBuilder):
  """Builder which generates a variety of stats from object information."""

  def _PrevObjs(self, obj):
    raise NotImplementedError

  @stat('total_volume', default=0)
  def TotalVolume(self, drink, prev):
    """Updates the total volume."""
    return float(drink.volume_ml) + prev

  @stat('total_count', default=0)
  def TotalPours(self, drink, prev):
    return prev + 1

  @stat('volume_avg')
  def AverageVolume(self, drink, prev):
    if prev is None:
      prev = {'count': 0, 'average': 0}
    res = prev.copy()
    vol = float(drink.Volume())
    res['average'] = (res['average']*res['count'] + vol) / (res['count'] + 1)
    res['count'] = res['count'] + 1
    return res

  @stat('volume_max')
  def LargestVolume(self, drink, prev):
    prev = {}
    if not prev:
      prev = {'volume': 0, 'id': 0}
    vol = float(drink.Volume())
    if prev.get('volume', 0) >= vol:
      return prev
    return {'volume': vol, 'id': drink.id}

  @stat('volume_min')
  def SmallestPour(self, drink, prev):
    prev = {}
    if not prev:
      prev = {'volume': 0, 'id': 0}
    vol = float(drink.Volume())
    if prev.get('volume', 0) < vol:
      return prev
    return {'volume': vol, 'id': drink.id}

  @stat('volume_by_day_of_week')
  def VolumeByDayOfweek(self, drink, prev):
    volmap = prev
    if not volmap:
      volmap = dict((i, 0) for i in xrange(7))
    # Note: uses the session's starttime, rather than the drink's. This causes
    # late-night sessions to be reported for the day on which they were started.
    weekday = drink.session.starttime.weekday()
    volmap[weekday] += float(drink.Volume())
    return volmap

  @stat('volume_by_drinker')
  def VolumeByDrinker(self, drink, prev):
    volmap = prev
    if not volmap:
      volmap = {}
    if drink.user:
      username = drink.user.username
    else:
      username = None
    volmap[username] = volmap.get(username, 0) + float(drink.Volume())
    return volmap

  @stat('registered_drinkers')
  def RegisteredDrinkers(self, drink, prev):
    if not prev:
      prev = []
    if drink.user and drink.user.username not in prev:
      prev.append(drink.user.username)
    return prev

  @stat('ids')
  def Ids(self, drink, prev):
    if prev is None:
      prev = []
    drink_id = drink.id
    if drink_id not in prev:
      prev.append(drink_id)
    return prev


class SystemStatsBuilder(BaseStatsBuilder):
  """Builder of systemwide stats by drink."""
  REVISION = 4

  def _PrevObjs(self, drink):
    qs = drink.site.drinks.valid().filter(seqn__lt=drink.seqn)
    qs = qs.order_by('seqn')
    return qs


class DrinkerStatsBuilder(BaseStatsBuilder):
  """Builder of user-specific stats by drink."""
  REVISION = 4

  def _PrevObjs(self, drink):
    qs = drink.user.drinks.valid().filter(endtime__lt=drink.endtime)
    qs = qs.order_by('endtime')
    return qs

  #@stat('volume-per-user-session')
  def VolumePerSession(self, drink, prev):
    if not prev:
      prev = []
    sess = drink.GetSession()
    user_sess = drink.user.session_parts.filter(session=sess)[0]
    res = [itertools.ifilter(lambda x: x[0] != user_sess.id, prev)]
    res.append((user_sess.id, float(user_sess.Volume())))


class KegStatsBuilder(BaseStatsBuilder):
  """Builder of keg-specific stats."""
  REVISION = 4

  def _PrevObjs(self, drink):
    qs = drink.keg.drinks.valid().filter(endtime__lt=drink.endtime)
    qs = qs.order_by('endtime')
    return qs

  @stat('drinkers')
  def Drinkers(self, drink, prev):
    if not prev:
      prev = []
    if drink.user and drink.user.id not in prev:
      prev.append(drink.user.id)
    return prev


class SessionStatsBuilder(BaseStatsBuilder):
  """Builder of user-specific stats by drink."""
  REVISION = 4

  def _PrevObjs(self, drink):
    qs = drink.session.drinks.valid().filter(endtime__lt=drink.endtime)
    qs = qs.order_by('endtime')
    return qs


def main():
  from pykeg.core import models

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

