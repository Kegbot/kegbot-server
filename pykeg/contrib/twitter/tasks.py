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

"""Celery tasks for Twitter."""

import os

import tweepy
from pykeg.celery import app
from pykeg.core.util import download_to_tempfile

from pykeg.plugin import util

logger = util.get_logger(__name__)


@app.task(name='twitter_tweet', expires=60)
def send_tweet(consumer_key, consumer_secret, oauth_token, oauth_token_secret, tweet, image_url):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, secure=True)
    auth.set_access_token(oauth_token, oauth_token_secret)
    api = tweepy.API(auth)

    local_media = None
    if image_url:
        try:
            local_media = download_to_tempfile(image_url)
        except IOError as e:
            logger.warning('Error downloading media url "%s": %s' % (image_url, e))

    if not local_media:
        logger.info('Sending text-only tweet: {}'.format(repr(tweet)))
        result = api.update_status(tweet)
    else:
        logger.info('Sending media tweet.')
        try:
            result = api.update_with_media(local_media, status=tweet)
        finally:
            os.unlink(local_media)
    return result
