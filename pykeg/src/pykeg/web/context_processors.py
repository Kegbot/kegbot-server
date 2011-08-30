from pykeg.core import features
from pykeg.core import models

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

def kbsite(request):
  ret = {}
  kbsite = request.kbsite
  ret['kbsite'] = kbsite
  if kbsite:
    kbsettings, _ = models.SiteSetting.objects.get_or_create(site=request.kbsite)
    ret['kbsettings'] = kbsettings
  return ret
