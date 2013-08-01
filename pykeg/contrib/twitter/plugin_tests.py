# Copyright 2013 Mike Wakerly <opensource@hoho.com>
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

import datetime

from unittest import TestCase
from pykeg.contrib.twitter import plugin

TAP_NAME = 'kegboard.flow0'

class FakeDatastore:
    def __init__(self):
        self.backing_dict = dict()

    def set(self, key, value):
        self.backing_dict[key] = value

    def get(self, key, default=None):
        return self.backing_dict.get(key, default)

    def delete(self, key):
        del self.backing_dict[key]

class TwitterPluginTestCase(TestCase):
    def setUp(self):
        self.datastore = FakeDatastore()
        self.backing_dict = self.datastore.backing_dict
        self.plugin = plugin.TwitterPlugin(self.datastore)

    def testTruncateTweet(self):
        msg = 'x'*138 + 'x'
        truncated = plugin.truncate_tweet(msg)
        self.assertEquals(msg, truncated)

        longer_msg = 'x'*138 + ' xxxx'
        truncated = plugin.truncate_tweet(longer_msg)
        self.assertEqual(139, len(truncated))
        self.assertEqual('x'*138 + plugin.TRUNCATE_STR, truncated)

    def testPluginBasics(self):
        self.assertEquals({}, self.plugin.get_site_profile())
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

if __name__ == '__main__':
    unittest.main()
