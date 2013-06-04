from django.conf import settings

import pykeg
from pykeg.core import features
from pykeg.core import models
from pykeg.web.kegweb.forms import LoginForm

def enabled_features(request):
  """Adds a USE_FEATURENAME flags for each enabled feature (see features.py)"""
  # TODO(mikey): this might make it harder to diagnose why features aren't
  # visible/being used.
  ret = {}
  ret['USE_FACEBOOK'] = features.use_facebook()
  ret['USE_FOURSQUARE'] = features.use_foursquare()
  ret['USE_TWITTER'] = features.use_twitter()
  ret['USE_UNTAPPD'] = features.use_untappd()
  return ret

def kbsite(request):
  kbsite = getattr(request, 'kbsite', None)

  ret = {
    'DEBUG': settings.DEBUG,
    'EPOCH': pykeg.EPOCH,
    'VERSION': pykeg.__version__,
    'HAVE_SESSIONS': False,
    'HAVE_ADMIN': settings.KEGBOT_ENABLE_ADMIN,
    'GOOGLE_ANALYTICS_ID': None,
    'kbsite': kbsite,
    'request_path': request.path,
    'login_form': LoginForm(initial={'next_page': request.path}),
    'guest_info': {
      'name': 'guest',
      'image': None,
    },
  }

  if kbsite:
    ret['guest_info']['name'] = kbsite.settings.guest_name
    ret['guest_info']['image'] = kbsite.settings.guest_image
    ret['SERIAL_NUMBER'] = kbsite.serial_number
    ret['HAVE_SESSIONS'] = models.DrinkingSession.objects.all().count() > 0
    ret['GOOGLE_ANALYTICS_ID'] = kbsite.settings.google_analytics_id

  return ret
