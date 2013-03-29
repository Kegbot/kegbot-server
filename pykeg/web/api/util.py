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
from django.db.models.query import QuerySet
from pykeg.proto import protolib
from kegbot.api import protoutil
from google.protobuf.message import Message

from kegbot.api import kbapi
from kegbot.util import kbjson
from pykeg.core import models
from pykeg.core import backend

from . import validate_jsonp

import logging
import sys
import traceback
import types

LOGGER = logging.getLogger(__name__)

def is_api_request(request):
  return request.path.startswith('/api')

def check_api_key(request):
  """Check a request for an API key."""
  keystr = request.META.get('HTTP_X_KEGBOT_API_KEY')
  if not keystr:
    keystr = request.REQUEST.get('api_key')
  if not keystr:
    raise kbapi.NoAuthTokenError('The parameter "api_key" is required')

  try:
    api_key = models.ApiKey.objects.get(key=keystr)
  except models.ApiKey.DoesNotExist:
    raise kbapi.BadApiKeyError('API key does not exist')

  if not api_key.is_active():
    raise kbapi.BadApiKeyError('Key and/or user is inactive')

  if not api_key.user or not api_key.user.is_active:
    raise kbapi.PermissionDeniedError('User is disabled or does not exist.')

  # TODO: remove me.
  if not api_key.user.is_staff and not api_key.user.is_superuser:
    raise kbapi.PermissionDeniedError('User is not staff/superuser')

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
  result = {
    'error' : {
      'code' : code,
      'message' : message
    }
  }
  if settings.DEBUG:
    result['error']['traceback'] = "".join(traceback.format_exception(*exc_info))
  return result, http_code

def build_response(result_data, response_code=200, callback=None):
  """Builds an HTTP response for JSON data."""
  indent = 2
  json_str = kbjson.dumps(result_data, indent=indent)
  if callback and validate_jsonp.is_valid_jsonp_callback_value(callback):
    json_str = '%s(%s);' % (callback, json_str)
  return HttpResponse(json_str, mimetype='application/json', status=response_code)


def prepare_data(data, inner=False):
  if isinstance(data, QuerySet) or type(data) == types.ListType:
    result = [prepare_data(d, True) for d in data]
    container = 'objects'
  elif isinstance(data, dict):
    result = data
    container = 'object'
  else:
    result = to_dict(data)
    container = 'object'

  if inner:
    return result
  else:
    return {
      container: result
    }

def to_dict(data):
  if not isinstance(data, Message):
    data = protolib.ToProto(data, full=True)
  return protoutil.ProtoMessageToDict(data)

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


