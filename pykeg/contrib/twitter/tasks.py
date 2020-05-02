"""Celery tasks for Twitter."""

import os

import tweepy
from pykeg.celery import app
from pykeg.core.util import download_to_tempfile

from pykeg.plugin import util

logger = util.get_logger(__name__)


@app.task(name="twitter_tweet", expires=60)
def send_tweet(consumer_key, consumer_secret, oauth_token, oauth_token_secret, tweet, image_url):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(oauth_token, oauth_token_secret)
    api = tweepy.API(auth)

    local_media = None
    if image_url:
        try:
            local_media = download_to_tempfile(image_url)
        except IOError as e:
            logger.warning('Error downloading media url "%s": %s' % (image_url, e))

    if not local_media:
        logger.info("Sending text-only tweet: {}".format(repr(tweet)))
        result = api.update_status(tweet)
    else:
        logger.info("Sending media tweet.")
        try:
            result = api.update_with_media(local_media, status=tweet)
        finally:
            os.unlink(local_media)
    return result
