from django.conf import settings

def enabled_features(request):
  """Adds a USE_FEATURENAME flags for each enabled feature.

  Currently defined:
    USE_FACEBOOK - Allow registration and fbconnect login via django-socialauth
    USE_TWITTER - pykeg.contrib.twitter is installed.
  """
  ret = {}

  # TODO(mikey): this might make it harder to diagnose why features aren't
  # visible/being used.
  if 'socialregistration' in settings.INSTALLED_APPS and \
      'facebook.djangofb.FacebookMiddleware' in settings.MIDDLEWARE_CLASSES and \
      'socialregistration.auth.FacebookAuth' in settings.AUTHENTICATION_BACKENDS and \
      getattr(settings, 'FACEBOOK_API_KEY', None) and \
      getattr(settings, 'FACEBOOK_SECRET_KEY', None):
    ret['USE_FACEBOOK'] = True

  if 'pykeg.contrib.twitter' in settings.INSTALLED_APPS:
    ret['USE_TWITTER'] = True

  return ret
