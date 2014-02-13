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
import tempfile
from contextlib import closing

import tweepy
import requests
from celery.task import task

from pykeg.plugin import util

logger = util.get_logger(__name__)

@task(expires=60)
def send_tweet(consumer_key, consumer_secret, oauth_token, oauth_token_secret, tweet, image_url):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, secure=True)
    auth.set_access_token(oauth_token, oauth_token_secret)
    api = tweepy.API(auth)

    if not image_url:
        logger.info('Sending text-only tweet: {}'.format(repr(tweet)))
        result = api.update_status(tweet)
    else:
        logger.info('Sending media tweet.')
        local_media = download_file(image_url)
        try:
            result = api.update_with_media(local_media, status=tweet)
        finally:
            os.unlink(local_media)
    return result

def download_file(url):
    r = requests.get(url, stream=True)
    ext = os.path.splitext(url)[1]
    fd, pathname = tempfile.mkstemp(suffix=ext)
    logger.info('Downloading file %s to path %s' % (url, pathname))
    with closing(os.fdopen(fd, 'wb')):
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                os.write(fd, chunk)
    return pathname

