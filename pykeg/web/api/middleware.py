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

def wrap_exception(request, exception):
  """Returns a HttpResponse with the exception in JSON form."""
  exc_info = sys.exc_info()

  LOGGER.error('%s: %s' % (exception.__class__.__name__, exception),
      exc_info=exc_info,
      extra={
        'status_code': 500,
        'request': request,
      }
  )

  # Don't wrap the exception during debugging.
  if settings.DEBUG and 'deb' in request.GET:
    return None

  if settings.HAVE_RAVEN:
    from raven.contrib.django.raven_compat.models import sentry_exception_handler
    sentry_exception_handler(request=request)

  result_data, http_code = util.to_json_error(exception, exc_info)
  result_data['meta'] = {
    'result': 'error'
  }
  return util.build_response(result_data, response_code=http_code)


class ApiRequestMiddleware:
  def process_request(self, request):
    request.is_kb_api_request = util.is_api_request(request)
    if not request.is_kb_api_request:
      # Not an API request. Skip me.
      return None
    try:
      if request.need_setup:
        raise ValueError('Setup required')
      elif request.need_upgrade:
        raise ValueError('Upgrade required')

      privacy = request.kbsite.settings.privacy
      if privacy == 'public':
        # API request, but public site privacy.  Views will check access as needed.
        return None
      elif request.path in ('/api/login/', '/api/get-api-key/'):
        # API request to whitelisted path.
        return None
      else:
        # API request to non-whitelisted path, in non-public site privacy mode.
        # Demand API key.
        if privacy == 'members' and request.user.is_authenticated():
          return None
        elif privacy == 'staff' and request.user.is_staff:
          return None
        util.check_api_key(request)
    except Exception, e:
      return wrap_exception(request, e)


class ApiResponseMiddleware:
  def process_exception(self, request, exception):
    """Wraps exceptions for API requests."""
    if util.is_api_request(request):
      return wrap_exception(request, exception)
    return None

  def process_response(self, request, response):
    if not util.is_api_request(request):
      return response

    if not isinstance(response, HttpResponse):
      data = util.prepare_data(response)
      data['meta'] = {
        'result': 'ok'
      }
      callback = request.GET.get('callback')
      response = util.build_response(data, 200, callback=callback)
    response['Cache-Control'] = 'max-age=0'
    return response
