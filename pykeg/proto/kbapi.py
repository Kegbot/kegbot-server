"""Kegweb API client."""

from builtins import object
import datetime
import sys
import requests
from .util import AttrDict

import logging
logging.getLogger('requests').setLevel(logging.WARNING)

from kegbot.api.exceptions import *
import json

import gflags

gflags.DEFINE_float('api_timeout', 10.0,
    'Socket timeout, in seconds, for Kegbot web API operations. '
    'Note that this timeout only applies to blocking socket operations '
    '(such as opening a connection) and not I/O.')

FLAGS = gflags.FLAGS

_DEFAULT_URL = 'http://localhost:8000/api/'
_DEFAULT_KEY = ''
try:
  from pykeg import settings
  if hasattr(settings, 'KEGWEB_BASE_URL'):
    _DEFAULT_URL = '%s/api/' % getattr(settings, 'KEGWEB_BASE_URL')
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

def decode_response(response):
  """Decodes the requests response object as a JSON response.

  For normal responses, the return value is the Python JSON-decoded 'result'
  field of the response.  If the response is an error, a RemoteError exception
  is raised.
  """

  status_code = response.status_code
  response_dict = response.json()

  if 'error' in response_dict:
    # Response had an error: translate to exception.
    err = response_dict['error']
    code = err.get('code', status_code)
    message = err.get('message', None)
    e = ErrorCodeToException(code, message)
    raise e
  elif 'object' in response_dict or 'objects' in response_dict:
    # Response was OK, return the result.
    return AttrDict(response_dict)
  else:
    # WTF?
    raise ValueError('Invalid response from server: missing result or error')

### end common

class Client(object):
  """Kegweb RESTful API client."""
  def __init__(self, api_url=None, api_key=None):
    if api_url is None:
      api_url = FLAGS.api_url
    if api_key is None:
      api_key = FLAGS.api_key
    self._api_url = api_url
    self._api_key = api_key

  def _get_url(self, endpoint):
    base = self._api_url.rstrip('/')
    endpoint = endpoint.strip('/')
    return '%s/%s' % (base, endpoint)

  def _http_get(self, endpoint, params=None):
    """Issues a GET request to the endpoint, and retuns the result.

    Keyword arguments are passed to the endpoint as GET arguments.

    For normal responses, the return value is the Python JSON-decoded 'object'
    or 'objects' field of the response.  If the response is an error, a
    RemoteError exception is raised.

    If there was an error contacting the server, or in parsing its response, a
    ServerError is raised.
    """
    return self._http_request(endpoint, params=params)

  def _http_post(self, endpoint, post_data, params=None):
    """Issues a POST request to the endpoint, and returns the result.

    For normal responses, the return value is the Python JSON-decoded 'object'
    or 'objects' field of the response.  If the response is an error, a
    RemoteError exception is raised.

    If there was an error contacting the server, or in parsing its response, a
    ServerError is raised.
    """
    return self._http_request(endpoint, params=params, post_data=post_data)

  def _http_request(self, endpoint, params=None, post_data=None):
    """Issues a POST or GET request, depending on the arguments."""
    headers = {
      'X-Kegbot-Api-Key': self._api_key,
    }
    url = self._get_url(endpoint)

    try:
      if post_data:
        r = requests.post(url, params=params, data=post_data, headers=headers,
            timeout=FLAGS.api_timeout)
      else:
        r = requests.get(url, params=params, headers=headers,
            timeout=FLAGS.api_timeout)
    except requests.exceptions.RequestException as e:
      raise RequestError(e)

    return decode_response(r)

  def record_drink(self, tap_name, ticks, volume_ml=None, username=None,
      pour_time=None, duration=0, auth_token=None, spilled=False, shout=''):
    endpoint = '/taps/%s' % tap_name
    post_data = {
      'tap_name': tap_name,
      'ticks': ticks,
    }
    if volume_ml is not None:
      post_data['volume_ml'] = volume_ml
    if username is not None:
      post_data['username'] = username
    if duration > 0:
      post_data['duration'] = duration
    if auth_token is not None:
      post_data['auth_token'] = auth_token
    if spilled:
      post_data['spilled'] = spilled
    if shout:
      post_data['shout'] = shout
    if pour_time:
      post_data['pour_time'] = int(pour_time.strftime('%s'))
      post_data['now'] = int(datetime.datetime.now().strftime('%s'))
    return self._http_post(endpoint, post_data=post_data).object

  def cancel_drink(self, seqn, spilled=False):
    endpoint = '/cancel-drink'
    post_data = {
      'id': seqn,
      'spilled': spilled,
    }
    return self._http_post(endpoint, post_data=post_data).object

  def log_sensor_reading(self, sensor_name, temperature, when=None):
    endpoint = '/thermo-sensors/%s' % (sensor_name,)
    post_data = {
      'temp_c': float(temperature),
    }
    # TODO(mikey): include post data
    return self._http_post(endpoint, post_data=post_data).object

  def status(self):
    """Gets complete system status."""
    return self._http_get('status').object

  def taps(self):
    """Gets the status of all taps."""
    return self._http_get('taps').objects

  def get_token(self, auth_device, token_value):
    url = 'auth-tokens/%s/%s' % (auth_device, token_value)
    try:
      return self._http_get(url).object
    except ServerError as e:
      raise NotFoundError(e)

  def drinks(self):
    """Gets a list of all drinks."""
    return self._http_get('drinks').objects

  def sound_events(self):
    """Gets a list of all sound events."""
    return self._http_get('sound-events').objects

  def create_controller(self, controller_name, model_name='unknown', serial_number='unknown'):
    post_data = {
      'name': controller_name,
      'model_name': model_name,
      'serial_number': serial_number,
    }
    return self._http_post('controllers', post_data=post_data).object

  def create_flow_meter(self, controller_id, port_name, ticks_per_ml=2.2):
    post_data = {
      'port_name': port_name,
      'controller': controller_id,
      'ticks_per_ml': ticks_per_ml,
    }
    return self._http_post('flow-meters', post_data=post_data).object
