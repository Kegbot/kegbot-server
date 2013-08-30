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

from django.test import TransactionTestCase

from kegbot.api import models_pb2
from kegbot.api.protoutil import ProtoMessageToDict
from kegbot.util import util

from . import backend
from . import models
from . import stats
from .testutils import make_datetime

class StatsTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.backend = backend.KegbotBackend()

        test_usernames = ('user1', 'user2', 'user3')
        self.users = [self.backend.create_new_user(name) for name in test_usernames]

        self.taps = [
            self.backend.create_tap('tap1', 'kegboard.flow0', ml_per_tick=1/2200.0),
            self.backend.create_tap('tap2', 'kegboard.flow1', ml_per_tick=1/2200.0),
        ]

        self.keg = self.backend.start_keg('kegboard.flow0', beer_name='Unknown',
            brewer_name='Unknown', style_name='Unknown')

    def testStuff(self):
        site = models.KegbotSite.get()
        stats = site.GetStats()
        self.assertEquals(stats, {})

        now = make_datetime(2012, 1, 2, 12, 00)
        self.maxDiff = None

        d = self.backend.record_drink('kegboard.flow0', ticks=1, volume_ml=100,
            username='user1', pour_time=now)
        expected = util.AttrDict({
            u'volume_by_year': {u'2012': 100.0},
            u'total_pours': 1,
            u'has_guest_pour': False,
            u'greatest_volume_ml': 100.0,
            u'registered_drinkers': [u'user1'],
            u'volume_by_day_of_week': {u'1': 100.0},
            u'greatest_volume_id': d.id,
            u'volume_by_drinker': {u'user1': 100.0},
            u'last_drink_id': d.id,
            u'sessions_count': 1,
            u'average_volume_ml': 100.0,
            u'total_volume_ml': 100.0
        })
        stats = site.GetStats()
        self.assertDictEqual(expected, stats)

        now = make_datetime(2012, 1, 3, 12, 00)
        d = self.backend.record_drink('kegboard.flow0', ticks=200,
            volume_ml=200, username='user2', pour_time=now)
        stats = site.GetStats()
        expected.total_pours = 2
        expected.greatest_volume_ml = 200.0
        expected.greatest_volume_id = d.id
        expected.registered_drinkers.append(u'user2')
        expected.volume_by_drinker[u'user2'] = 200.0
        expected.last_drink_id = d.id
        expected.average_volume_ml = 150.0
        expected.total_volume_ml = 300.0
        expected.volume_by_day_of_week[u'2'] = 200.0
        expected.volume_by_year[u'2012'] = 300.0
        expected.sessions_count = 2
        print 'EXPECTED'
        import pprint
        pprint.pprint(expected)
        print '----'
        print 'ACTUAL'
        pprint.pprint(stats)
        self.assertDictEqual(expected, stats)
