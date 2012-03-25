# Copyright 2012 Mike Wakerly <opensource@hoho.com>
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

from pykeg.core import kbjson
from pykeg.core import util

from urllib import urlencode
import urllib2
import logging
import tweepy
from django.contrib.sites.models import Site

from celery.decorators import task

from . import util

@task
def tweet_event(event):
  if should_tweet(event):
    do_tweet(event)
    return True
  return False

def should_tweet(event):
  if event.kind not in ('session_joined', 'drink_poured'):
    print 'Event not tweetable: %s' % event
    return False

  return True

def add_hashtag(tweet):
  if len(tweet) <= (140 - len(util.HASHTAG) - 1):
    tweet = '%s %s' % (tweet, util.HASHTAG)
  return tweet

def _get_vars(event):
  base_url = 'http://%s/%s' % (Site.objects.get_current().domain, event.site.url())
  name = ''
  if event.user:
    name = event.user.username
  session_url = ''
  drink_url = ''

  if event.drink:
    session_url = '%s/%s' % (base_url, event.drink.session.get_absolute_url())
    drink_url = event.drink.ShortUrl()

  beer_name = ''
  if event.drink.keg and event.drink.keg.type:
    beer_name = event.drink.keg.type.name

  drink_size = ''
  if event.drink:
    drink_size = '%.1foz' % event.drink.Volume().InOunces()

  kbvars = {
    'kb_name': event.site.settings.title,
    'name': name,
    'kb_url': base_url,
    'drink_url': drink_url,
    'session_url': session_url,
    'drink_size': drink_size,
    'beer_name': beer_name,
  }
  return kbvars

def do_tweet(event):
  kbvars = _get_vars(event)
  do_user_tweet(event, kbvars)
  do_system_tweet(event, kbvars)

def do_system_tweet(event, kbvars):
  """Sends a tweet using the system's account (if any)."""
  system_profile = util.get_site_profile(event.site)
  if not system_profile:
    print 'No system twitter profile, skipping system tweet'
    return

  name = 'Someone'
  user = event.user
  if user:
    name = user.username
    user_profile = util.get_user_profile(user)
    if user_profile:
      name = '@%s' % (user_profile.settings.twitter_name,)
  kbvars['name'] = name

  system_api = util.get_api(system_profile.oauth_token,
      system_profile.oauth_token_secret)

  tweet = None
  if event.kind == 'session_joined':
    tweet = util.DEFAULT_SYSTEM_SESSION_JOINED_TEMPLATE % kbvars
  elif event.kind == 'drink_poured':
    tweet = util.DEFAULT_SYSTEM_DRINK_POURED_TEMPLATE % kbvars

  if tweet:
    tweet = add_hashtag(tweet)
    print 'Sending system tweet: %s' % tweet
    try:
      ret = system_api.update_status(tweet)
    except tweepy.TweepError, e:
      print e

def do_user_tweet(event, kbvars):
  """Sends a tweet using the user's account (if any)."""
  user = event.user
  if not user:
    return

  profile = util.get_user_profile(user)
  if not profile or not profile.settings.enabled:
    print 'User has disabled Twitter'
    return

  kind = event.kind
  tweet = None
  if kind == 'drink_poured':
    if not profile.settings.post_drink_poured:
      print 'User has disabled drink pour tweets: %s' % event.user
      return
    tweet = util.DEFAULT_USER_SESSION_JOINED_TEMPLATE % kbvars
  elif kind == 'session_joined':
    if not profile.settings.post_session_joined:
      print 'User has disabled session-join tweets: %s' % event.user
      return
    tweet = util.DEFAULT_USER_DRINK_POURED_TEMPLATE % kbvars

  user_api = util.get_api(profile.access_token.oauth_token,
      profile.access_token.oauth_token_secret)

  if tweet:
    tweet = add_hashtag(tweet)
    print 'Sending user tweet: %s' % tweet
    try:
      ret = user_api.update_status(tweet)
    except tweepy.TweepError, e:
      print e
