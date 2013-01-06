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

"""Utilities for processing API views."""

from django.conf import settings
from django.http import Http404
from django.http import HttpResponse

from kegbot.api import kbapi
from kegbot.util import kbjson
from pykeg.core import models
from pykeg.core.backend import backend
from . import apikey

import logging
import sys
import traceback

LOGGER = logging.getLogger(__name__)

ATTR_API_VIEW = 'api_view'
ATTR_API_REQUEST = 'api_request'
ATTR_API_AUTHENTICATED = 'api_authenticated'
ATTR_API_AUTH_REQUIRED = 'api_auth_required'

def is_api_view(view):
  return getattr(view, ATTR_API_VIEW, False)

def set_is_api_view(view):
  setattr(view, ATTR_API_VIEW, True)

def is_api_request(request):
  return getattr(request, ATTR_API_REQUEST, False)

def set_is_api_request(request):
  setattr(request, ATTR_API_REQUEST, True)

def request_is_authenticated(request):
  return getattr(request, ATTR_API_AUTHENTICATED, False)

def set_request_is_authenticated(request):
  setattr(request, ATTR_API_AUTHENTICATED, True)

def view_requires_authentication(view):
  return getattr(view, ATTR_API_AUTH_REQUIRED, False)

def set_view_requires_authentication(view):
  setattr(view, ATTR_API_AUTH_REQUIRED, True)

def check_api_key(request):
  """Check a request for an API key."""
  keystr = request.META.get('HTTP_X_KEGBOT_API_KEY')
  if not keystr:
    keystr = request.REQUEST.get('api_key')
  if not keystr:
    raise kbapi.NoAuthTokenError('The parameter "api_key" is required')

  try:
    key = apikey.ApiKey.FromString(keystr)
  except ValueError, e:
    raise kbapi.BadApiKeyError('Error parsing API key: %s' % e)

  try:
    user = models.User.objects.get(pk=key.uid())
  except models.User.DoesNotExist:
    raise kbapi.BadApiKeyError('API user %s does not exist' % key.uid())

  if not user.is_active:
    raise kbapi.BadApiKeyError('User is inactive')

  if not user.is_staff and not user.is_superuser:
    raise kbapi.PermissionDeniedError('User is not staff/superuser')

  user_secret = user.get_profile().api_secret
  if not user_secret or user_secret != key.secret():
    raise kbapi.BadApiKeyError('User secret does not match')

  setattr(request, ATTR_API_AUTHENTICATED, True)


def to_json_error(e, exc_info):
  """Converts an exception to an API error response."""
  # Wrap some common exception types into kbapi types
  if isinstance(e, Http404):
    e = kbapi.NotFoundError(e.message)
  elif isinstance(e, ValueError):
    e = kbapi.BadRequestError(str(e))
  elif isinstance(e, backend.NoTokenError):
    e = kbapi.NotFoundError(e.message)

  # Now determine the response based on the exception type.
  if isinstance(e, kbapi.Error):
    code = e.__class__.__name__
    http_code = e.HTTP_CODE
    message = e.Message()
  else:
    code = 'ServerError'
    http_code = 500
    message = 'An internal error occurred: %s' % str(e)
    if settings.DEBUG:
      message += "\n" + "\n".join(traceback.format_exception(*exc_info))
  result = {
    'error' : {
      'code' : code,
      'message' : message
    }
  }
  return result, http_code

def build_response(result_data, response_code=200):
  """Builds an HTTP response for JSON data."""
  indent = 2
  return HttpResponse(kbjson.dumps(result_data, indent=indent),
      mimetype='application/json', status=response_code)

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

  result_data, http_code = to_json_error(exception, exc_info)
  result_data['meta'] = {
    'result': 'error'
  }
  return build_response(result_data, response_code=http_code)


