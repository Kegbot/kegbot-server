from django.conf import settings

"""Methods to query configuration of optional features."""

def use_facebook():
  if not getattr(settings, 'FACEBOOK_API_KEY', ''):
    return False
  if not getattr(settings, 'FACEBOOK_SECRET_KEY', ''):
    return False
  return True

def use_twitter():
  if not getattr(settings, 'TWITTER_CONSUMER_KEY', ''):
    return False
  if not getattr(settings, 'TWITTER_CONSUMER_SECRET_KEY', ''):
    return False
  return True

def use_foursquare():
  if not getattr(settings, 'FOURSQUARE_CLIENT_ID', ''):
    return False
  if not getattr(settings, 'FOURSQUARE_CLIENT_SECRET', ''):
    return False
  return True

def use_untappd():
  if not getattr(settings, 'UNTAPPD_CLIENT_ID', ''):
    return False
  if not getattr(settings, 'UNTAPPD_CLIENT_SECRET', ''):
    return False
  return True
