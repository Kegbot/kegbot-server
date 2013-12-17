from django.conf import settings

import pykeg
from pykeg.core import models
from pykeg.core import util
from pykeg.web.kegweb.forms import LoginForm

def kbsite(request):
    kbsite = getattr(request, 'kbsite', None)

    ret = {
      'DEBUG': settings.DEBUG,
      'EMBEDDED': getattr(settings, 'EMBEDDED', False),
      'EPOCH': pykeg.EPOCH,
      'VERSION': util.get_version(),
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
      'PLUGINS': getattr(request, 'plugins', {}),
    }

    if kbsite:
        ret['guest_info']['name'] = kbsite.settings.guest_name
        ret['guest_info']['image'] = kbsite.settings.guest_image
        ret['SERIAL_NUMBER'] = kbsite.serial_number
        ret['HAVE_SESSIONS'] = models.DrinkingSession.objects.all().count() > 0
        ret['GOOGLE_ANALYTICS_ID'] = kbsite.settings.google_analytics_id

    return ret
