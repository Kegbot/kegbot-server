from django.conf import settings

import urllib

from pykeg.core import models
from pykeg.core import util
from pykeg.web.kegweb.forms import LoginForm


def kbsite(request):
    kbsite = getattr(request, 'kbsite', None)

    redir = urllib.urlencode({'redir': request.build_absolute_uri(request.path)})

    sso_login_url = getattr(settings, 'SSO_LOGIN_URL', '')
    if sso_login_url:
        sso_login_url = '{}?{}'.format(sso_login_url, redir)

    sso_logout_url = getattr(settings, 'SSO_LOGOUT_URL', '')
    if sso_logout_url:
        sso_logout_url = '{}?{}'.format(sso_logout_url, redir)

    ret = {
        'DEBUG': settings.DEBUG,
        'DEMO_MODE': settings.DEMO_MODE,
        'EMBEDDED': settings.EMBEDDED,
        'VERSION': util.get_version(),
        'HAVE_SESSIONS': False,
        'HAVE_ADMIN': settings.KEGBOT_ENABLE_ADMIN,
        'GOOGLE_ANALYTICS_ID': None,
        'SSO_LOGIN_URL': sso_login_url,
        'SSO_LOGOUT_URL': sso_logout_url,
        'CAN_INVITE': kbsite.can_invite(request.user) if kbsite else False,
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
        ret['HAVE_SESSIONS'] = models.DrinkingSession.objects.all().count() > 0
        ret['GOOGLE_ANALYTICS_ID'] = kbsite.google_analytics_id
        ret['metric_volumes'] = (kbsite.volume_display_units == 'metric')
        ret['temperature_display_units'] = kbsite.temperature_display_units

    return ret
