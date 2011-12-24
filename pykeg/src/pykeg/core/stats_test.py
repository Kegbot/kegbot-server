# Copyright 2003-2011 Mike Wakerly <opensource@hoho.com>
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

import datetime

from django.utils import unittest

from pykeg.core import backend
from pykeg.core import models
from pykeg.core import stats
from pykeg.proto import models_pb2
from pykeg.proto.protoutil import ProtoMessageToDict

class StatsTestCase(unittest.TestCase):
  def setUp(self):
    self.site, created = models.KegbotSite.objects.get_or_create(name='default')
    self.backend = backend.KegbotBackend(site=self.site)

    test_usernames = ('user1', 'user2', 'user3')
    self.users = [self.backend.CreateNewUser(name) for name in test_usernames]

    self.taps = [
        self.backend.CreateTap('tap1', 'kegboard.flow0', ml_per_tick=1/2200.0),
        self.backend.CreateTap('tap2', 'kegboard.flow1', ml_per_tick=1/2200.0),
    ]

    #self.drinks = []
    #for user in self.users:
    #  for amt in (100, 200, 300):
    #    d = self.backend.RecordDrink('kegboard.flow0', ticks=amt,
    #        volume_ml=amt, username=user.username, do_postprocess=False)
    #    self.drinks.append(d)

  def assertProtosEqual(self, expected, actual):
    d1 = ProtoMessageToDict(expected)
    d2 = ProtoMessageToDict(actual)
    msg = ''
    for k, v in d1.iteritems():
      if k not in d2:
        msg += 'Value for %s not present in actual. \n' % k
      elif v != d2[k]:
        msg += 'Values for %s differ: expected "%s", actual "%s". \n' % (k, v, d2[k])
    for k, v in d2.iteritems():
      if k not in d1:
        msg += 'Value for %s not present in expected. \n' % k
    if msg:
      self.fail(msg)

  def _getEmptyStats(self):
    s = models_pb2.Stats()
    s.last_drink_id = "0"
    s.total_volume_ml = 0.0
    s.total_pours = 0
    s.average_volume_ml = 0.0
    s.greatest_volume_ml = 0.0
    s.greatest_volume_id = "0"
    return s

  def testStuff(self):
    builder = stats.SystemStatsBuilder(None)

    empty_stats = models_pb2.Stats()
    system_stats_d0 = builder.Build()
    self.assertEquals(empty_stats, system_stats_d0)

    # Record a new drink and verify stats.
    pour_time = datetime.datetime(2011, 05, 01, 12, 00)
    self.backend.RecordDrink('kegboard.flow0', ticks=100,
        volume_ml=100, username='user1', pour_time=pour_time,
        do_postprocess=False)
    drink1 = models.Drink.objects.get(seqn=1)

    expected = self._getEmptyStats()
    expected.last_drink_id = "1"
    expected.total_volume_ml = 100.0
    expected.total_pours = 1
    expected.average_volume_ml = 100.0
    expected.greatest_volume_ml = 100.0
    expected.greatest_volume_id = "1"
    expected.has_guest_pour = False
    d = expected.volume_by_day_of_week.add()
    d.weekday = "0"  # Sunday
    d.volume_ml = 100
    u = expected.volume_by_drinker.add()
    u.username = "user1"
    u.volume_ml = 100
    y = expected.volume_by_year.add()
    y.year = 2011
    y.volume_ml = 100
    expected.registered_drinkers.append("user1")
    expected.sessions_count = 1

    system_stats_d1 = stats.SystemStatsBuilder(drink1).Build()
    self.assertProtosEqual(expected, system_stats_d1)

    # Pour another drink
    self.backend.RecordDrink('kegboard.flow0', ticks=200,
        volume_ml=200, username='user1', pour_time=pour_time,
        do_postprocess=False)
    drink2 = models.Drink.objects.get(seqn=2)

    # Adjust stats
    expected.last_drink_id = "2"
    expected.total_volume_ml = 300.0
    expected.total_pours = 2
    expected.average_volume_ml = 150.0
    expected.greatest_volume_ml = 200.0
    expected.greatest_volume_id = "2"
    d = expected.volume_by_day_of_week[0]
    d.volume_ml += 200
    u = expected.volume_by_drinker[0]
    u.volume_ml += 200
    y = expected.volume_by_year[0]
    y.volume_ml += 200

    system_stats_d2 = stats.SystemStatsBuilder(drink2).Build()
    self.assertProtosEqual(expected, system_stats_d2)

    # Build the same stats incrementally and verify identical result.
    system_stats_d2_inc = stats.SystemStatsBuilder(drink2, system_stats_d1).Build()
    self.assertProtosEqual(system_stats_d2, system_stats_d2_inc)

