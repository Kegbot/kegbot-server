# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

"""Kegweb API client."""

import datetime
import functools
import socket
import sys
import types
import urllib2

from pykeg.core import kbjson
from pykeg.proto import api_pb2
from pykeg.proto import models_pb2
from pykeg.proto import protoutil

import urllib2
from urllib import urlencode
from urllib2 import HTTPError
from urllib2 import URLError

import gflags

gflags.DEFINE_float('krest_timeout', 10.0,
    'Socket timeout, in seconds, for Kegbot web API operations. '
    'Note that this timeout only applies to blocking socket operations '
    '(such as opening a connection) and not I/O.')

FLAGS = gflags.FLAGS

_DEFAULT_URL = 'http://localhost:8001/api/'
_DEFAULT_KEY = ''
try:
  from pykeg import settings
  if hasattr(settings, 'KEGWEB_BASE_URL'):
    _DEFAULT_URL = '%s/api' % getattr(settings, 'KEGWEB_BASE_URL')
  if hasattr(settings, 'KEGWEB_API_KEY'):
    _DEFAULT_KEY = settings.KEGWEB_API_KEY
except ImportError:
  # Non-fatal if we can't load settings.
  pass

gflags.DEFINE_string('api_url', _DEFAULT_URL,
    'Base URL for the Kegweb HTTP api.')

gflags.DEFINE_string('api_key', _DEFAULT_KEY,
    'Access key for the Kegweb HTTP api.')

### begin common

class Error(Exception):
  """An error occurred."""
  HTTP_CODE = 400
  def Message(self):
    if self.message:
      return self.message
    m = self.__class__.__doc__
    m = m.split('\n', 1)[0]
    return m

class NotFoundError(Error):
  """The requested object could not be found."""
  HTTP_CODE = 404

class ServerError(Error):
  """The server had a problem fulfilling your request."""
  HTTP_CODE = 500

class BadRequestError(Error):
  """The request was incompleted or malformed."""
  HTTP_CODE = 401

class NoAuthTokenError(Error):
  """An api_key is required."""
  HTTP_CODE = 401

class BadAuthTokenError(Error):
  """The api_key given is invalid."""
  HTTP_CODE = 401

class PermissionDeniedError(Error):
  """The api_key given does not have permission for this resource."""
  HTTP_CODE = 401

MAP_NAME_TO_EXCEPTION = dict((c.__name__, c) for c in Error.__subclasses__())

def ErrorCodeToException(code, message=None):
  cls = MAP_NAME_TO_EXCEPTION.get(code, Error)
  return cls(message)

def decode_response(response_data, out_msg):
  """Decodes the string `response_data` as a JSON response.

  For normal responses, the return value is the Python JSON-decoded 'result'
  field of the response.  If the response is an error, a RemoteError exception
  is raised.
  """
  # Decode JSON.
  try:
    d = kbjson.loads(response_data)
  except ValueError, e:
    raise ServerError('Malformed response: %s' % e)

  if 'error' in d:
    # Response had an error: translate to exception.
    err = d.get('error', {})
    code = err.get('code', 'Unknown')
    message = err.get('message', None)
    e = ErrorCodeToException(code, message)
    raise e
  elif 'result' in d:
    # Response was OK, return the result.
    result = d.get('result')
    if out_msg:
      return protoutil.DictToProtoMessage(result, out_msg)
    else:
      return None
  else:
    # WTF?
    raise ValueError('Invalid response from server: missing result or error')

### end common

class KrestClient:
  """Kegweb RESTful API client."""
  def __init__(self, api_url=None, api_key=None):
    if api_url is None:
      api_url = FLAGS.api_url
    if api_key is None:
      api_key = FLAGS.api_key
    self._api_url = api_url
    self._api_key = api_key
    self._opener = urllib2.build_opener(KrestHTTPErrorProcessor)

  def _Encode(self, s):
    return unicode(s).encode('utf-8')

  def _EncodePostData(self, post_data):
    if not post_data:
      return None
    return urlencode(dict(((k, self._Encode(v)) for k, v in
        post_data.iteritems() if v is not None)))

  def _GetURL(self, endpoint, params=None):
    param_str = ''
    if params:
      param_str = '?%s' % urlencode(params)

    base = self._api_url.rstrip('/')

    # Strip both leading and trailing slash from endpoint: single leading and
    # trailing slashes will be added by the string formatter.  (The trailing
    # slash is required for POSTs to Django.)
    endpoint = endpoint.strip('/')
    return '%s/%s/%s' % (base, endpoint, param_str)

  def SetAuthToken(self, api_key):
    self._api_key = api_key

  def DoGET(self, endpoint, out_msg, params=None):
    """Issues a GET request to the endpoint, and retuns the result.

    Keyword arguments are passed to the endpoint as GET arguments.

    For normal responses, the return value is the Python JSON-decoded 'result'
    field of the response.  If the response is an error, a RemoteError exception
    is raised.

    If there was an error contacting the server, or in parsing its response, a
    ServerError is raised.
    """
    return self._FetchResponse(endpoint, out_msg, params=params)

  def DoPOST(self, endpoint, out_msg, post_data, params=None):
    """Issues a POST request to the endpoint, and returns the result.

    For normal responses, the return value is the Python JSON-decoded 'result'
    field of the response.  If the response is an error, a RemoteError exception
    is raised.

    If there was an error contacting the server, or in parsing its response, a
    ServerError is raised.
    """
    return self._FetchResponse(endpoint, out_msg, params=params, post_data=post_data)

  def _FetchResponse(self, endpoint, out_msg, params=None, post_data=None):
    """Issues a POST or GET request, depending on the arguments."""
    if params is None:
      params = {}
    else:
      params = params.copy()

    # If we have an api token, attach it.  Prefer to attach it to POST data, but
    # use GET if there is no POST data.
    if self._api_key:
      if post_data:
        post_data['api_key'] = self._api_key
      else:
        params['api_key'] = self._api_key

    url = self._GetURL(endpoint, params=params)
    encoded_post_data = self._EncodePostData(post_data)

    try:
      # Issue a GET or POST (urlopen will decide based on encoded_post_data).
      response_data = self._opener.open(url, data=encoded_post_data,
          timeout=FLAGS.krest_timeout).read()
    except HTTPError, e:
      raise ServerError('Caused by: %s' % e)
    except URLError, e:
      raise ServerError('URL Error, reason: %s' % e.reason)

    return decode_response(response_data, out_msg)

  def RecordDrink(self, tap_name, ticks, volume_ml=None, username=None,
      pour_time=None, duration=0, auth_token=None, spilled=False):
    endpoint = '/taps/%s' % tap_name
    post_data = {
      'tap_name': tap_name,
      'ticks': ticks,
      'volume_ml': volume_ml,
      'username': username,
      'auth_token': auth_token,
      'duration': duration,
      'spilled': spilled,
    }
    if pour_time:
      post_data['pour_time'] = int(pour_time.strftime('%s'))
      post_data['now'] = int(datetime.datetime.now().strftime('%s'))
    return self.DoPOST(endpoint, models_pb2.Drink(), post_data=post_data)

  def CancelDrink(self, seqn, spilled=False):
    endpoint = '/cancel-drink'
    post_data = {
      'id': seqn,
      'spilled': spilled,
    }
    return self.DoPOST(endpoint, models_pb2.Drink(), post_data=post_data)

  def LogSensorReading(self, sensor_name, temperature, when=None):
    endpoint = '/thermo-sensors/%s' % (sensor_name,)
    post_data = {
      'temp_c': float(temperature),
    }
    # TODO(mikey): include post data
    return self.DoPOST(endpoint, models_pb2.ThermoLog(), post_data=post_data)

  def TapStatus(self):
    """Gets the status of all taps."""
    return self.DoGET('taps', api_pb2.TapDetailSet())

  def GetToken(self, auth_device, token_value):
    url = 'auth-tokens/%s.%s' % (auth_device, token_value)
    try:
      return self.DoGET(url, models_pb2.AuthenticationToken())
    except ServerError, e:
      raise NotFoundError(e)

  def LastDrinks(self):
    """Gets a list of the most recent drinks."""
    return self.DoGET('last-drinks', api_pb2.DrinkSet())

  def AllDrinks(self):
    """Gets a list of all drinks."""
    return self.DoGET('drinks', api_pb2.DrinkSet())

  def AllSoundEvents(self):
    """Gets a list of all drinks."""
    return self.DoGET('sound-events', api_pb2.SoundEventSet())

class KrestHTTPErrorProcessor(urllib2.BaseHandler):
  def _handle_error(self, request, response, code, msg, hdrs):
    data = response.read()
    decode_response(data, None)

  http_error_401 = _handle_error
  http_error_403 = _handle_error
  http_error_404 = _handle_error
  http_error_405 = _handle_error
  http_error_500 = _handle_error

def main():
  c = KrestClient()

  print '== record a drink =='
  print c.RecordDrink('kegboard.flow0', 2200)
  print ''

  print '== tap status =='
  for t in c.TapStatus().taps:
    print t
    print ''

  print '== last drinks =='
  for d in c.LastDrinks().drinks:
    print d
    print ''

if __name__ == '__main__':
  FLAGS(sys.argv)
  main()
