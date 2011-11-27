# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

"""Post-drink Twitter annoy-o-matic.

To enable, you must:
- set `feature.twitter.enable` to TRUE in the Config table;
- set `contrib.twitter.login_name` and `contrib.twitter.login_pass` in Config to
  the user you want to use for tweets;
- add `pykeg.contrib.twitter` to the INSTALLED_APPS list (in the settings file);
- syncdb
"""

import random

from pykeg.core import backend
from pykeg.core import kb_app
from pykeg.core import models as core_models
from pykeg.core.net import kegnet
from pykeg.contrib.twitter import models

import twitter

TWITTER_NAME_UNKNOWN = 'Someone'
TWEET_MAX_LEN = 140

TWEET_TEMPLATE = (
    '%(tweet_to)s just poured %(ounces).1f oz'
    '%(keg_predicate)s.'
    '%(smug_remark)s %(url)s %(trailer)s'
)

class TwitterKegnetClient(kegnet.SimpleKegnetClient):
  def __init__(self, addr=None):
    kegnet.SimpleKegnetClient.__init__(self, addr)
    self._backend = backend.KegbotBackend()

  def onDrinkCreated(self, event):
    self._logger.info('Processing new drink %i for user %s' % (event.drink_id,
        event.username))

    # TODO(mikey): this should not be allowed to use the DB directly. Quick hack
    # for now..
    drink = core_models.Drink.objects.get(id=event.drink_id)

    tweet_to = TWITTER_NAME_UNKNOWN
    if drink.user:
      try:
        db_user = core_models.User.objects.get(username=drink.user.username)
        profile = db_user.get_profile()
      except (core_models.User.DoesNotExist, core_models.UserProfile.DoesNotExist):
        self._logger.warning('Profile for user %s does not exist' % (drink.user,))
        return
      try:
        twitter_link = models.UserTwitterLink.objects.get(user_profile=profile)
        tweet_to = '@' + twitter_link.twitter_name
        # TODO(mikey): determine if the user is following us; refuse to tweet if
        # not (so as to avoid tweeting @SomeRandomUser)
        # TODO(mikey): follow users who have established a link
      except models.UserTwitterLink.DoesNotExist:
        # Twitter name unknown: use kegbot username (with no '@')
        self._logger.warning('User %s has not enabled twitter link.' % (drink.user,))
        tweet_to = drink.user.username
    else:
      config = self._backend.GetConfig()
      if not config.getboolean('contrib.twitter.tweet_unknown'):
        self._logger.info('Tweeting for unknown users is disabled.')
        return

    tweet = self._GenerateTweet(drink, tweet_to)
    if not tweet:
      return

    try:
      tweet_log = self._DoTweet(tweet)
      models.DrinkTweetLog.objects.create(tweet_log=tweet_log, drink=drink)
    except Exception, e:
      self._logger.warning('Error posting tweet: %s' % (e,))
      return

    self._logger.info('Tweet posted: id=%s text="%s"' % (tweet_log.twitter_id,
        tweet_log.tweet))

  def _DoTweet(self, tweet):
    config = self._backend.GetConfig()
    twitter_name = config.get('contrib.twitter.login_name')
    twitter_pass = config.get('contrib.twitter.login_pass')

    # compress extra spaces
    tweet = ' '.join(tweet.split())

    if not twitter_name or not twitter_pass:
      self._logger.warning('No twitter login credentials')
      return

    api = twitter.Api(username=twitter_name, password=twitter_pass)
    api.SetXTwitterHeaders('Kegbot', 'http://kegbot.org/', '1.0')
    self._logger.info('Posting tweet [%i]: "%s"' % (len(tweet), tweet))
    status = api.PostUpdate(tweet)

    tweet_log = models.TweetLog.objects.create(twitter_id=str(status.id),
        tweet=tweet)
    return tweet_log

  def _GenerateTweet(self, drink, tweet_to):
    ounces = drink.Volume().InOunces()
    config = self._backend.GetConfig()

    try:
      min_ounces = float(config.get('contrib.twitter.min_oz'))
    except (TypeError, ValueError):
      min_ounces = 2.0

    if ounces < min_ounces:
      self._logger.info('Drink too small to care about; no tweet for you!')
      return

    smug_remark = models.DrinkRemark.GetRemarkForDrink(drink)
    if smug_remark:
      smug_remark = ' ' + smug_remark.remark
    else:
      smug_remark = ''
    trailer = ' #kegbot'

    keg_predicate = ''
    if drink.keg:
      keg_name = drink.keg.type.name
      if keg_name:
        keg_predicate = ' of %s' % drink.keg.type.name

    url = drink.ShortUrl()

    full_tweet = TWEET_TEMPLATE % vars()
    smug_remark = ''
    small_tweet = TWEET_TEMPLATE % vars()
    keg_predicate = ''
    tiny_tweet = TWEET_TEMPLATE % vars()

    self._logger.debug('Full tweet [%i]: %s' % (len(full_tweet), full_tweet))
    self._logger.debug('Small tweet [%i]: %s' % (len(small_tweet), small_tweet))
    self._logger.debug('Tiny tweet [%i]: %s' % (len(tiny_tweet), tiny_tweet))

    if len(full_tweet) < TWEET_MAX_LEN:
      return full_tweet
    elif len(small_tweet) < TWEET_MAX_LEN:
      return small_tweet
    elif len(tiny_weet) < TWEET_MAX_LEN:
      return tiny_tweet
    else:
      self._logger.error('All tweets were too large.')
      return ''


class TwitterApp(kb_app.App):
  def _MainLoop(self):
    self._client = TwitterKegnetClient()
    while not self._do_quit:
      self._client.serve_forever()

  def Quit(self):
    kb_app.App.Quit(self)
    self._client.stop()
