from django.conf import settings

"""Methods to query configuration of optional features."""

def use_facebook():
  return 'socialregistration' in settings.INSTALLED_APPS and \
      'facebook.djangofb.FacebookMiddleware' in settings.MIDDLEWARE_CLASSES and \
      'socialregistration.auth.FacebookAuth' in settings.AUTHENTICATION_BACKENDS and \
      getattr(settings, 'FACEBOOK_API_KEY', None) is not None and \
      getattr(settings, 'FACEBOOK_SECRET_KEY', None) is not None

def use_twitter():
  return 'pykeg.contrib.twitter' in settings.INSTALLED_APPS
