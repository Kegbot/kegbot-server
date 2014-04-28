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

"""Unittests for Twitter plugin."""

from django.test import TransactionTestCase
from pykeg.contrib.twitter import plugin
from pykeg.plugin.datastore import InMemoryDatastore

from pykeg.core import models


class TwitterPluginTestCase(TransactionTestCase):

    def setUp(self):
        self.datastore = InMemoryDatastore(plugin.TwitterPlugin.get_short_name())
        self.plugin = plugin.TwitterPlugin(datastore=self.datastore)
        self.user = models.User.objects.create(username='twitter_test')

    def test_plugin(self):
        self.assertEqual({}, self.plugin.get_site_profile())
        self.assertEqual({}, self.plugin.get_user_profile(self.user))

        fake_profile = {
            plugin.KEY_OAUTH_TOKEN: '1',
            plugin.KEY_OAUTH_TOKEN_SECRET: '2',
            plugin.KEY_TWITTER_NAME: '3',
            plugin.KEY_TWITTER_ID: '4',
        }
        self.plugin.save_site_profile('1', '2', '3', '4')
        self.assertEquals(fake_profile, self.plugin.get_site_profile())
        self.plugin.remove_site_profile()
        self.assertEquals({}, self.plugin.get_site_profile())
        self.plugin.save_site_profile('1', '2', '3', '4')

    def test_get_site_twitter_settings_form(self):
        settings_form = self.plugin.get_site_twitter_settings_form()
        expected = {
            'tweet_keg_events': True,
            'tweet_session_events': True,
            'tweet_drink_events': False,
            'include_guests': True,
            'include_pictures': False,
            'append_url': True,
            'keg_started_template': 'Woot! Just tapped a new keg of $BEER!',
            'keg_ended_template': 'The keg of $BEER has been finished.',
            'session_started_template': '$DRINKER kicked off a new session on $SITENAME.',
            'session_joined_template': '$DRINKER joined the session.',
            'drink_poured_template': '$DRINKER poured $VOLUME of $BEER on $SITENAME.',
            'user_drink_poured_template': 'Just poured $VOLUME of $BEER on $SITENAME. #kegbot',
        }
        self.assertEquals(expected, dict(settings_form.initial))

    def test_truncate_tweet(self):
        msg = 'x' * 138 + 'x'
        truncated = plugin.truncate_tweet(msg)
        self.assertEquals(msg, truncated)

        longer_msg = 'x' * 138 + ' xxxx'
        truncated = plugin.truncate_tweet(longer_msg)
        self.assertEqual(139, len(truncated))
        self.assertEqual('x' * 138 + plugin.TRUNCATE_STR, truncated)
