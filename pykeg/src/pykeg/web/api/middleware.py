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

  if settings.DEBUG and settings.HAVE_RAVEN:
    from raven.contrib.django.models import client
    client.captureException()

  # Don't wrap the exception during debugging.
  if settings.DEBUG and 'deb' in request.GET:
    return None

  result_data, http_code = util.to_json_error(exception, exc_info)
  result_data['meta'] = {
    'result': 'error'
  }
  return util.build_response(result_data, response_code=http_code)


class WrapExceptionMiddleware:
  """Translates responses and exceptions to JSON."""
  def process_view(self, request, view_func, view_args, view_kwargs):
    if util.is_api_view(view_func):
      util.set_is_api_request(request)

  def process_exception(self, request, exception):
    if not util.is_api_request(request):
      return None
    return wrap_exception(request, exception)


class CheckAccessMiddleware:
  def process_view(self, request, view_func, view_args, view_kwargs):
    if not util.is_api_view(view_func):
      return None

    if not util.request_is_authenticated(request):
      if util.view_requires_authentication(view_func):
        try:
          util.check_api_key(request)
        except Exception, e:
          return wrap_exception(request, e)
