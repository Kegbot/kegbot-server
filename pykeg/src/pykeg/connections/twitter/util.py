from django.conf import settings
from socialregistration.contrib.twitter import models as sr_twitter_models
import tweepy

from . import models

_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET_KEY', '')

HEADERS = {
  'User-Agent': 'Kegbot',
}

# Available template vars:
#   name         : user name, or @twitter_name if known
#   kb_name      : kegbot system name
#   kb_url       : kegbot system url
#   session_url  : current session url
#   drink_url    : drink url (if any)
#   drink_size   : drink size
#   beer_name    : beer name

DEFAULT_USER_SESSION_JOINED_TEMPLATE = "I'm having a drink on %(kb_name)s! %(kb_url)s"
DEFAULT_USER_DRINK_POURED_TEMPLATE = "I just poured %(drink_size)s of %(beer_name)s on %(kb_name)s! %(drink_url)s"

DEFAULT_SYSTEM_SESSION_JOINED_TEMPLATE = "%(name)s is having a drink on %(kb_name)s! %(kb_url)s"
DEFAULT_SYSTEM_DRINK_POURED_TEMPLATE = "%(name)s just poured %(drink_size)s of %(beer_name)s on %(kb_name)s! %(drink_url)s"

# Appended if space is permitting.
HASHTAG = "#kegbot"

def get_api(oauth_token, oauth_token_secret):
  auth = tweepy.OAuthHandler(_CONSUMER_KEY, _CONSUMER_SECRET)
  auth.set_access_token(oauth_token, oauth_token_secret)
  return tweepy.API(auth)

def update_site_status(site, tweet):
  return update_status(site.twitter_profile.oauth_token,
      site.twitter_profile.oauth_token_secret, tweet)

def update_status(oauth_token, oauth_token_secret, tweet):
  api = get_api(oauth_token, oauth_token_secret)
  return api.update_status(tweet, headers=HEADERS)

def get_user_profile(user):
  try:
    return sr_twitter_models.TwitterProfile.objects.get(user=user)
  except sr_twitter_models.TwitterProfile.DoesNotExist:
    return None

def get_site_profile(site):
  try:
    return models.SiteTwitterProfile.objects.get(site=site)
  except models.SiteTwitterProfile.DoesNotExist:
    return None
