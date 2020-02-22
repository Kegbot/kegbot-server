# Copyright 2014 Bevbot LLC, All Rights Reserved
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

from pykeg.backend import get_kegbot_backend
from pykeg.core import models
from pykeg import config
from pykeg.core.util import get_version_object
from pykeg.core.util import set_current_request
from pykeg.core.util import must_upgrade
from pykeg.web.api.util import is_api_request

from pykeg.plugin import util as plugin_util

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

# Requests are always allowed for these path prefixes.
PRIVACY_EXEMPT_PATHS = (
    '/account/activate',
    '/accounts/',
    '/admin/',
    '/media/',
    '/setup/',
    '/sso/login',
    '/sso/logout',
)

PRIVACY_EXEMPT_PATHS += getattr(settings, 'KEGBOT_EXTRA_PRIVACY_EXEMPT_PATHS', ())


def _path_allowed(path, kbsite):
    for p in PRIVACY_EXEMPT_PATHS:
        if path.startswith(p):
            return True
    return False


class CurrentRequestMiddleware(object):
    """Set/clear the current request."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        try:
            response = self.get_response(request)
        finally:
            set_current_request(None)
        return response


class IsSetupMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not config.is_setup():
            # Disable the auth user middleware.
            request.session = {}
            request.session['_auth_user_backend'] = None

            if not request.path.startswith('/setup'):
                return render(request, 'setup_wizard/setup_required.html', status=403)
        return self.get_response(request)


class KegbotSiteMiddleware(object):
    ALLOWED_VIEW_MODULE_PREFIXES = (
        'pykeg.web.setup_wizard.',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.need_setup = False
        request.need_upgrade = False
        request.kbsite = None

        installed_version = models.KegbotSite.get_installed_version()
        if installed_version is None:
            request.need_setup = True
        else:
            request.installed_version_string = str(installed_version)
            request.need_upgrade = must_upgrade(installed_version, get_version_object())

        if not request.need_setup and not request.need_upgrade:
            request.kbsite = models.KegbotSite.objects.get(name='default')
            if request.kbsite.is_setup:
                timezone.activate(request.kbsite.timezone)
                request.plugins = dict((p.get_short_name(), p)
                                       for p in plugin_util.get_plugins().values())
            else:
                request.need_setup = True
            request.backend = get_kegbot_backend()

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        for prefix in self.ALLOWED_VIEW_MODULE_PREFIXES:
            if view_func.__module__.startswith(prefix):
                return None

        if is_api_request(request):
            # API endpoints handle "setup required" differently.
            return None

        if request.need_setup:
            return self._setup_required(request)
        elif request.need_upgrade:
            return self._upgrade_required(request)

        return None

    def _setup_required(self, request):
        return render(request, 'setup_wizard/setup_required.html', status=403)

    def _upgrade_required(self, request):
        context = {
            'installed_version': getattr(request, 'installed_version_string', None),
        }
        return render(request, 'setup_wizard/upgrade_required.html',
                      context=context, status=403)


class PrivacyMiddleware(object):
    """Enforces site privacy settings.

    Must be installed after ApiRequestMiddleware (in request order) to
    access is_kb_api_request attribute.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not hasattr(request, 'kbsite'):
            return None
        elif _path_allowed(request.path, request.kbsite):
            return None
        elif request.is_kb_api_request:
            # api.middleware will enforce access requirements.
            return None

        privacy = request.kbsite.privacy

        if privacy == 'public':
            return None
        elif privacy == 'staff':
            if not request.user.is_staff:
                return render(request, 'kegweb/staff_only.html', status=401)
            return None
        elif privacy == 'members':
            if not request.user.is_authenticated() or not request.user.is_active:
                return render(request, 'kegweb/members_only.html', status=401)
            return None

        return HttpResponse(
            'Server misconfigured, unknown privacy setting:%s' %
            privacy, status=500)
