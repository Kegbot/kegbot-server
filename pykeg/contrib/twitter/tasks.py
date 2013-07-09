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

"""Celery tasks for Twitter."""

import tweepy
from celery.task import task

from pykeg.plugin import util

logger = util.get_logger(__name__)

@task(expires=60)
def send_tweet(consumer_key, consumer_secret, oauth_token, oauth_token_secret, tweet):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(oauth_token, oauth_token_secret)
    api = tweepy.API(auth)
    logger.info('Sending tweet: {}'.format(repr(tweet)))
    result = api.update_status(tweet)
    return result
