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

from django.test import TransactionTestCase
from django.test.utils import override_settings

from kegbot.util import util

from . import models
from .testutils import make_datetime

import copy
from pykeg.backend import get_kegbot_backend


@override_settings(KEGBOT_BACKEND='pykeg.core.testutils.TestBackend')
class StatsTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.backend = get_kegbot_backend()
        models.User.objects.create_user('guest')

        test_usernames = ('user1', 'user2', 'user3')
        self.users = [self.backend.create_new_user(name, '%s@example.com' % name) for name in test_usernames]

        self.taps = [
            self.backend.create_tap('tap1', 'kegboard.flow0', ticks_per_ml=2.2),
            self.backend.create_tap('tap2', 'kegboard.flow1', ticks_per_ml=2.2),
        ]

        self.keg = self.backend.start_keg('kegboard.flow0', beverage_name='Unknown',
            beverage_type='beer', producer_name='Unknown', style_name='Unknown')

    def testStuff(self):
        site = models.KegbotSite.get()
        stats = site.get_stats()
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
            u'volume_by_session': {u'1': 100.0},
            u'last_drink_id': d.id,
            u'keg_ids': [d.keg.id],
            u'sessions_count': 1,
            u'average_volume_ml': 100.0,
            u'total_volume_ml': 100.0,
            u'largest_session': {u'session_id': 1, u'volume_ml': 100},
        })
        stats = site.get_stats()
        self.assertDictEqual(expected, stats)

        now = make_datetime(2012, 1, 3, 12, 00)
        d = self.backend.record_drink('kegboard.flow0', ticks=200,
            volume_ml=200, username='user2', pour_time=now)
        stats = site.get_stats()
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
        expected.volume_by_session = {u'1': 100.0, u'2': 200.0}
        expected.largest_session = {u'session_id': 2, u'volume_ml': 200.0}

        self.assertDictEqual(expected, stats)

        d = self.backend.record_drink('kegboard.flow0', ticks=300,
            volume_ml=300, username='user2', pour_time=now)

        stats = site.get_stats()
        expected.total_pours = 3
        expected.greatest_volume_ml = 300.0
        expected.greatest_volume_id = d.id
        expected.volume_by_drinker[u'user2'] = 500.0
        expected.last_drink_id = d.id
        expected.average_volume_ml = 200.0
        expected.total_volume_ml = 600.0
        expected.volume_by_day_of_week[u'2'] = 500.0
        expected.volume_by_year[u'2012'] = 600.0
        expected.sessions_count = 2
        expected.volume_by_session = {u'1': 100.0, u'2': 500.0}
        expected.largest_session = {u'session_id': 2, u'volume_ml': 500.0}

        self.assertDictEqual(expected, stats)
        previous_stats = copy.copy(stats)

        d = self.backend.record_drink('kegboard.flow0', ticks=300,
            volume_ml=300, pour_time=now)

        stats = site.get_stats()
        self.assertTrue(stats.has_guest_pour)

        self.backend.cancel_drink(d)
        stats = site.get_stats()

        self.assertDictEqual(previous_stats, stats)

    def test_cancel_and_reassign(self):
        drink_data = [
            (100, self.users[0]),
            (200, self.users[1]),
            (200, self.users[2]),
            (500, self.users[0]),
        ]

        drinks = []

        now = make_datetime(2012, 1, 2, 12, 00)
        for volume_ml, user in drink_data:
            d = self.backend.record_drink('kegboard.flow0', ticks=volume_ml,
                username=user.username, volume_ml=volume_ml, pour_time=now)
            drinks.append(d)

        self.assertEquals(600, self.users[0].get_stats().total_volume_ml)
        self.assertEquals(200, self.users[1].get_stats().total_volume_ml)
        self.assertEquals(200, self.users[2].get_stats().total_volume_ml)

        self.assertEquals(1000, models.KegbotSite.get().get_stats().total_volume_ml)

        self.backend.cancel_drink(drinks[0])
        self.assertEquals(500, self.users[0].get_stats().total_volume_ml)
        self.assertEquals(200, self.users[1].get_stats().total_volume_ml)
        self.assertEquals(200, self.users[2].get_stats().total_volume_ml)
        self.assertEquals(900, models.KegbotSite.get().get_stats().total_volume_ml)

        self.backend.assign_drink(drinks[1], self.users[0])
        self.assertEquals(700, self.users[0].get_stats().total_volume_ml)
        self.assertEquals({}, self.users[1].get_stats())
        self.assertEquals(200, self.users[2].get_stats().total_volume_ml)
        self.assertEquals(900, models.KegbotSite.get().get_stats().total_volume_ml)
        self.assertEquals(900, drinks[1].session.get_stats().total_volume_ml)

        # Start a new session.
        now = make_datetime(2013, 1, 2, 12, 00)
        for volume_ml, user in drink_data:
            d = self.backend.record_drink('kegboard.flow0', ticks=volume_ml,
                username=user.username, volume_ml=volume_ml, pour_time=now)
            drinks.append(d)

        self.assertEquals(1300, self.users[0].get_stats().total_volume_ml)
        self.assertEquals(200, self.users[1].get_stats().total_volume_ml)
        self.assertEquals(400, self.users[2].get_stats().total_volume_ml)
        self.assertEquals(1900, models.KegbotSite.get().get_stats().total_volume_ml)
        self.assertEquals(1000, drinks[-1].session.get_stats().total_volume_ml)

        # Delete all stats for some intermediate drinks.
        models.Stats.objects.filter(drink=drinks[-1]).delete()
        models.Stats.objects.filter(drink=drinks[-2]).delete()

        d = self.backend.record_drink('kegboard.flow0', ticks=1111,
            username=user.username, volume_ml=1111, pour_time=now)
        drinks.append(d)

        # Intermediate stats are generated.
        self.assertEquals(3011, models.KegbotSite.get().get_stats().total_volume_ml)
        self.assertEquals(2111, drinks[-1].session.get_stats().total_volume_ml)
