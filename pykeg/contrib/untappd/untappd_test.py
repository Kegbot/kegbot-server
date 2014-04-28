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

"""Unittests for Untappd plugin."""

from mock import patch

from django.test import TransactionTestCase
from django.utils import timezone
from pykeg.contrib.untappd import plugin
from pykeg.contrib.foursquare.plugin import FoursquarePlugin
from pykeg.plugin.datastore import InMemoryDatastore

from pykeg.core import models
from pykeg.backend import get_kegbot_backend


class UntappdTests(TransactionTestCase):

    def setUp(self):
        self.datastore = InMemoryDatastore(plugin.UntappdPlugin.get_short_name())

        self.fsq = FoursquarePlugin(datastore=self.datastore)
        self.fake_plugin_registry = {'foursquare': self.fsq}

        self.plugin = plugin.UntappdPlugin(datastore=self.datastore,
            plugin_registry=self.fake_plugin_registry)
        self.user = models.User.objects.create(username='untappd_test')
        self.backend = get_kegbot_backend()
        self.tap = self.backend.create_tap('Test Tap', 'test.flow0')
        self.keg = self.backend.start_keg(tap=self.tap, beverage_name='Test Beer',
            beverage_type='beer', producer_name='Test Producer', style_name='Test Style')
        self.beverage = self.keg.type
        self.beverage.untappd_beer_id = '9876'
        self.beverage.save()

    def test_plugin(self):
        self.assertEqual((None, None), self.plugin.get_credentials())
        self.assertEqual({}, self.plugin.get_user_profile(self.user))

        fake_profile = {
            'foo': 'bar'
        }
        self.plugin.save_user_profile(self.user, fake_profile)
        self.assertEquals(fake_profile, self.plugin.get_user_profile(self.user))

    def test_drink_poured_no_foursquare(self):
        self.plugin.save_user_token(self.user, 'fake-token')
        self.assertEqual('fake-token', self.plugin.get_user_token(self.user))

        fake_drink = models.Drink.objects.create(keg=self.keg, volume_ml=1000, ticks=1000,
            user=self.user, time=timezone.now(), shout='Hello')
        fake_event = models.SystemEvent.objects.create(kind=models.SystemEvent.DRINK_POURED,
            drink=fake_drink, user=self.user, keg=self.keg, time=fake_drink.time)

        with patch('pykeg.contrib.untappd.tasks.untappd_checkin.delay') as mock_checkin:
            self.plugin.handle_new_events([fake_event])
            mock_checkin.assert_called_with('fake-token', '9876', 'UTC', shout='Hello',
                foursquare_client_id=None,
                foursquare_client_secret=None,
                foursquare_venue_id=None)

    def test_drink_poured_with_foursquare(self):
        fsq_settings = self.fsq.get_site_settings_form()
        fsq_settings.cleaned_data = {
            'venue_id': '54321',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-client-secret',
        }
        self.fsq.save_site_settings_form(fsq_settings)

        self.plugin.save_user_token(self.user, 'fake-token')
        self.assertEqual('fake-token', self.plugin.get_user_token(self.user))

        fake_drink = models.Drink.objects.create(keg=self.keg, volume_ml=1000, ticks=1000,
            user=self.user, time=timezone.now(), shout='Hello2')
        fake_event = models.SystemEvent.objects.create(kind=models.SystemEvent.DRINK_POURED,
            drink=fake_drink, user=self.user, keg=self.keg, time=fake_drink.time)

        with patch('pykeg.contrib.untappd.tasks.untappd_checkin.delay') as mock_checkin:
            self.plugin.handle_new_events([fake_event])
            mock_checkin.assert_called_with('fake-token', '9876', 'UTC', shout='Hello2',
                foursquare_client_id='fake-client-id',
                foursquare_client_secret='fake-client-secret',
                foursquare_venue_id='54321')
