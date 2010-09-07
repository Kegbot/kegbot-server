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
import sys
import types

from pykeg import settings
from pykeg.core import models_pb2
from pykeg.core.protoutil import DictToProtoMessage
from pykeg.web.api import common

try:
  from urllib.parse import urlencode
  from urllib.request import urlopen
  from urllib.error import URLError
except ImportError:
  from urllib import urlencode
  from urllib2 import urlopen
  from urllib2 import URLError

try:
  import json
except ImportError:
  try:
    import simplejson as json
  except ImportError:
    import django.utils.simplejson as json

import gflags
FLAGS = gflags.FLAGS

_DEFAULT_URL = 'http://localhost:8000/api/'
if hasattr(settings, 'KEGWEB_BASE_URL'):
  _DEFAULT_URL = '%s/api' % getattr(settings, 'KEGWEB_BASE_URL')

gflags.DEFINE_string('krest_url', _DEFAULT_URL,
    'Base URL for the Kegweb HTTP api.')

class ApiError(Exception):
  """Raised when the remote side returns an error."""

class ServerError(ApiError):
  """Raised when a malformed response is received from the server."""

class RemoteError(ApiError):
  """Raised when the remote API raises an error."""
  def __init__(self, code, message=None):
    self.code = code
    self.message = message


class KrestClient:
  """Kegweb RESTful API client."""
  def __init__(self, base_url=None, api_auth_token=None):
    if not base_url:
      base_url = FLAGS.krest_url
    self._base_url = base_url
    self._api_auth_token = api_auth_token

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

    base = self._base_url.rstrip('/')

    # Strip both leading and trailing slash from endpoint: single leading and
    # trailing slashes will be added by the string formatter.  (The trailing
    # slash is required for POSTs to Django.)
    endpoint = endpoint.strip('/')
    return '%s/%s/%s' % (base, endpoint, param_str)

  def SetAuthToken(self, api_auth_token):
    self._api_auth_token = api_auth_token

  def DoGET(self, endpoint, params=None):
    """Issues a GET request to the endpoint, and retuns the result.

    Keyword arguments are passed to the endpoint as GET arguments.

    For normal responses, the return value is the Python JSON-decoded 'result'
    field of the response.  If the response is an error, a RemoteError exception
    is raised.

    If there was an error contacting the server, or in parsing its response, a
    ServerError is raised.
    """
    return self._FetchResponse(endpoint, params=params)

  def DoPOST(self, endpoint, post_data, params=None):
    """Issues a POST request to the endpoint, and returns the result.

    For normal responses, the return value is the Python JSON-decoded 'result'
    field of the response.  If the response is an error, a RemoteError exception
    is raised.

    If there was an error contacting the server, or in parsing its response, a
    ServerError is raised.
    """
    return self._FetchResponse(endpoint, params=params, post_data=post_data)

  def _FetchResponse(self, endpoint, params=None, post_data=None):
    """Issues a POST or GET request, depending on the arguments."""
    if params is None:
      params = {}
    else:
      params = params.copy()

    # Request a full response, unless caller specified otherwise.
    if params and 'full' in params:
      if params['full'] != 0:
        params['full'] = 1
    else:
      params['full'] = 1

    # If we have an api token, attach it.  Prefer to attach it to POST data, but
    # use GET if there is no POST data.
    if self._api_auth_token:
      if post_data:
        post_data['api_auth_token'] = self._api_auth_token
      else:
        params['api_auth_token'] = self._api_auth_token

    url = self._GetURL(endpoint, params=params)
    encoded_post_data = self._EncodePostData(post_data)

    try:
      # Issue a GET or POST (urlopen will decide based on encoded_post_data).
      response_data = urlopen(url, encoded_post_data).read()
    except URLError, e:
      raise ServerError('Caused by: %s' % e)

    return self._DecodeResponse(response_data)

  def _DecodeResponse(self, response_data):
    """Decodes the string `response_data` as a JSON response.

    For normal responses, the return value is the Python JSON-decoded 'result'
    field of the response.  If the response is an error, a RemoteError exception
    is raised.
    """
    # Decode JSON.
    try:
      d = json.loads(response_data)
    except ValueError, e:
      raise ServerError('Malformed response: %s' % e)

    if 'error' in d:
      # Response had an error: translate to exception.
      err = d.get('error')
      if type(err) != types.DictType:
        raise ValueError('Invalid error response from server')
      code = err.get('code', 'Error')
      message = err.get('message', None)
      e = common.ErrorCodeToException(code, message)
      raise e
    elif 'result' in d:
      # Response was OK, return the result.
      return d.get('result')
    else:
      # WTF?
      raise ValueError('Invalid response from server: missing result or error')

  def _DictListToProtoList(self, d_list, proto_obj):
    return [DictToProtoMessage(m, proto_obj) for m in d_list]

  def RecordDrink(self, tap_name, ticks, volume_ml=None, username=None,
      pour_time=None, duration=None, auth_token=None):
    endpoint = '/tap/%s' % tap_name
    post_data = {
      'tap_name' : tap_name,
      'ticks' : ticks,
      'volume_ml' : volume_ml,
      'username' : username,
      'auth_token' : auth_token,
    }
    if pour_time:
      post_data['pour_time'] = pour_time
      post_data['now'] = datetime.datetime.now()
    return self.DoPOST(endpoint, post_data=post_data)

  def LogSensorReading(self, sensor_name, temperature, when=None):
    endpoint = '/thermo-sensor/%s' % (sensor_name,)
    post_data = {
      'temp_c': float(temperature),
    }
    # TODO(mikey): include post data
    res = self.DoPOST(endpoint, post_data=post_data)
    ret = DictToProtoMessage(res, models_pb2.ThermoLog)
    return ret

  def TapStatus(self, full=True):
    """Gets the status of all taps."""
    params = {'full' : full}
    response = self.DoGET('tap', params)
    return self._DictListToProtoList(response, models_pb2.KegTap())

  def GetToken(self, auth_device, token_value, full=True):
    url = 'auth-token/%s.%s' % (auth_device, token_value)
    params = {'full' : full}
    response = self.DoGET(url, params)
    return DictToProtoMessage(response, models_pb2.AuthenticationToken())

  def LastDrinks(self, full=True):
    """Gets a list of the most recent drinks."""
    params = {'full' : full}
    response = self.DoGET('last-drinks', params)
    return self._DictListToProtoList(response, models_pb2.Drink())

  def AllDrinks(self, full=True):
    """Gets a list of all drinks."""
    params = {'full' : full}
    response = self.DoGET('drink', params)
    return self._DictListToProtoList(response, models_pb2.Drink())


def main():
  c = KrestClient()

  print '== record a drink =='
  print c.RecordDrink('kegboard.flow0', 2200)
  print ''

  print '== tap status =='
  for t in c.TapStatus():
    print t
    print ''

  print '== last drinks =='
  for d in c.LastDrinks():
    print d
    print ''

if __name__ == '__main__':
  FLAGS(sys.argv)
  main()
