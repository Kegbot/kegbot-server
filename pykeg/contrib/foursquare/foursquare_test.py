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

"""Unittests for Foursquare plugin."""

from mock import patch

from django.test import TransactionTestCase
from django.utils import timezone
from pykeg.contrib.foursquare import plugin
from pykeg.plugin.datastore import InMemoryDatastore

from pykeg.core import models
from pykeg.backend import get_kegbot_backend


class FoursquareTests(TransactionTestCase):

    def setUp(self):
        self.datastore = InMemoryDatastore(plugin.FoursquarePlugin.get_short_name())
        self.plugin = plugin.FoursquarePlugin(datastore=self.datastore)
        self.user = models.User.objects.create(username='foursquare_test')
        self.backend = get_kegbot_backend()
        self.tap = self.backend.create_tap('Test Tap', 'test.flow0')
        self.keg = self.backend.start_keg(tap=self.tap, beverage_name='Test Beer',
            beverage_type='beer', producer_name='Test Producer', style_name='Test Style')

        fsq_settings = self.plugin.get_site_settings_form()
        fsq_settings.cleaned_data = {
            'venue_id': '54321',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-client-secret',
        }
        self.plugin.save_site_settings_form(fsq_settings)

    def test_plugin(self):
        self.assertEqual(('fake-client-id', 'fake-client-secret'), self.plugin.get_credentials())
        self.assertEqual({}, self.plugin.get_user_profile(self.user))
        fake_profile = {
            'foo': 'bar'
        }
        self.plugin.save_user_profile(self.user, fake_profile)
        self.assertEquals(fake_profile, self.plugin.get_user_profile(self.user))

    def test_drink_poured(self):
        self.plugin.save_user_token(self.user, '')
        self.assertEqual('', self.plugin.get_user_token(self.user))

        fake_drink = models.Drink.objects.create(keg=self.keg, volume_ml=1000, ticks=1000,
            user=self.user, time=timezone.now(), shout='Hello')
        fake_event = models.SystemEvent.objects.create(kind=models.SystemEvent.DRINK_POURED,
            drink=fake_drink, user=self.user, keg=self.keg, time=fake_drink.time)

        with patch('pykeg.contrib.foursquare.tasks.foursquare_checkin.delay') as mock_checkin:
            self.assertFalse(mock_checkin.called, 'Checkin should not have been called')

        self.plugin.save_user_token(self.user, 'fake-token')
        with patch('pykeg.contrib.foursquare.tasks.foursquare_checkin.delay') as mock_checkin:
            self.plugin.handle_new_events([fake_event])
            mock_checkin.assert_called_with('fake-token', '54321')
