from pykeg.core import features

def enabled_features(request):
  """Adds a USE_FEATURENAME flags for each enabled feature.

  Currently defined:
    USE_FACEBOOK - Allow registration and fbconnect login via django-socialauth
    USE_TWITTER - pykeg.contrib.twitter is installed.
  """
  # TODO(mikey): this might make it harder to diagnose why features aren't
  # visible/being used.
  ret = {}
  ret['USE_FACEBOOK'] = features.use_facebook()
  ret['USE_TWITTER'] = features.use_twitter()
  return ret
