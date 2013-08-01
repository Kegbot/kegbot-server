# Copyright 2012 Mike Wakerly <opensource@hoho.com>
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

from django.conf import settings
from django.http import HttpResponse

from . import util

import logging
import sys

LOGGER = logging.getLogger(__name__)

class ApiRequestMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        request.is_kb_api_request = util.is_api_request(request)
        if not request.is_kb_api_request:
            # Not an API request. Skip me.
            return None

        try:
            if request.need_setup:
                raise ValueError('Setup required')
            elif request.need_upgrade:
                raise ValueError('Upgrade required')

            need_auth = util.needs_auth(view_func)
            privacy = request.kbsite.settings.privacy
            if request.path in ('/api/login/', '/api/get-api-key/'):
                # API request to whitelisted path.
                need_auth = False
            else:
                # API request to non-whitelisted path, in non-public site privacy mode.
                # Demand API key.
                if privacy == 'members' and not request.user.is_authenticated():
                    need_auth = True
                elif privacy == 'staff' and not request.user.is_staff:
                    need_auth = True

            if need_auth:
                util.check_api_key(request)

            if request.method == 'GET':
                cached = request.kbcache.gen_get(cache_key(request))
                if cached:
                    response = util.build_response(request, cached, 200)
                    response.is_from_cache = True
                    return response

            return None

        except Exception, e:
            return util.wrap_exception(request, e)


class ApiResponseMiddleware:
    def process_exception(self, request, exception):
        """Wraps exceptions for API requests."""
        if util.is_api_request(request):
            return util.wrap_exception(request, exception)
        return None

    def process_response(self, request, response):
        if not util.is_api_request(request):
            return response

        if not isinstance(response, HttpResponse):
            data = util.prepare_data(response)
            data['meta'] = {
              'result': 'ok'
            }
            response = util.build_response(request, data, 200)

            if request.method == 'GET' and response.status_code == 200:
                if not getattr(response, 'is_from_cache', False):
                    request.kbcache.gen_set(cache_key(request), data)
        response['Cache-Control'] = 'max-age=0'
        return response


def cache_key(request):
    return 'api:%s' % request.get_full_path()
