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

import urlparse

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect


class DemoModeMiddleware:
    """Denies non-GET requests when in demo mode.."""
    WHITELISTED_PATHS = (
        '/accounts/login/',
        '/accounts/logout/',
        '/demo/',
    )

    def process_request(self, request):
        if not getattr(settings, 'DEMO_MODE', False):
            return
        if request.method == 'GET':
            return
        for path in self.WHITELISTED_PATHS:
            if request.path.startswith(path):
                return

        messages.error(request, 'Site is in demo mode; changes were not saved.')
        path_or_url = urlparse.urlparse(request.META.get('HTTP_REFERER', '')).path
        if not path_or_url:
            path_or_url = 'kb-home'

        return redirect(path_or_url)
