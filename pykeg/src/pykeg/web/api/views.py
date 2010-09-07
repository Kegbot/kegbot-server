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

"""Kegweb RESTful API views."""

from functools import wraps
import hashlib
import sys

try:
  import json
except ImportError:
  try:
    import simplejson as json
  except ImportError:
    try:
      from django.utils import simplejson as json
    except ImportError:
      raise ImportError, "Unable to load a json library"

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import Context
from django.template.loader import get_template

from pykeg.core import backend
from pykeg.core import models
from pykeg.core import protolib
from pykeg.core import protoutil
from pykeg.web.api import common
from pykeg.web.api import forms

from google.protobuf.message import Message

INDENT = 2

### Authentication

AUTH_KEY_BASE = None
AUTH_KEY = None
if hasattr(settings, 'KEGBOT_API_AUTH_SECRET') and \
    settings.KEGBOT_API_AUTH_SECRET:
  AUTH_KEY_BASE = settings.KEGBOT_API_AUTH_SECRET
elif hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY:
  AUTH_KEY_BASE = settings.SECRET_KEY

if AUTH_KEY_BASE:
  _m = hashlib.sha256()
  _m.update(AUTH_KEY_BASE)
  AUTH_KEY = _m.hexdigest()

### Decorators

def auth_required(viewfunc):
  def _check_token(request, *args, **kwargs):
    # Check for api_auth_token; allow in either POST or GET arguments.
    tok = request.REQUEST.get('api_auth_token')
    if not tok:
      raise common.NoAuthTokenError
    if tok.lower() == AUTH_KEY.lower():
      return viewfunc(request, *args, **kwargs)
    else:
      print repr(tok.lower())
      print repr(AUTH_KEY.lower())
      raise common.BadAuthTokenError
  return wraps(viewfunc)(_check_token)

def ToJsonError(e):
  """Converts an exception to an API error response."""
  if isinstance(e, common.Error):
    code = e.__class__.__name__
    message = e.Message()
  elif isinstance(e, ValueError):
    code = 'BadRequestError'
    message = str(e)
  else:
    code = 'ServerError'
    message = 'An internal error occurred: %s' % str(e)
  result = {
    'error' : {
      'code' : code,
      'message' : message
    }
  }
  return result

def obj_to_dict(o, with_full=False):
  if hasattr(o, '__iter__'):
    return [protoutil.ProtoMessageToDict(protolib.ToProto(x, with_full)) for x in o]
  else:
    return protoutil.ProtoMessageToDict(protolib.ToProto(o, with_full))

def py_to_json(f):
  """Decorator that wraps an API method.

  The decorator transforms the method in a few ways:
    - The raw return value from the method is converted to a serialized JSON
      result.
    - The result is wrapped in an outer dict, and set as the value 'result'
    - If an exception is thrown during the method, it is converted to a protocol
      error message.
  """
  def new_function(*args, **kwargs):
    try:
      try:
        result = {'result' : f(*args, **kwargs)}
      except Http404, e:
        # We might change the HTTP status code here one day.  This also allows
        # the views to use Http404 (rather than NotFound).
        raise common.NotFoundError(e.message)
      data = json.dumps(result, indent=INDENT)
    except Exception, e:
      result = ToJsonError(e)
      data = json.dumps(result, indent=INDENT)
    return HttpResponse(data, mimetype='application/json')
  return new_function

def model_to_py(f):
  """Decorator which converts method results to native types.

  The wrapped function should return either a single Django model instance, an
  iterable of the same, or a protocol buffer Message.

  This is a bit roundabount and inefficient:  Django model instances are first
  converted to protocol buffers, then to base python types, and finally to a
  JSON-formatted string.

  TODO(mikey): revisit this layering as the API matures, or once a kegbot site
  needs to handle >0.1 qps :)
  """
  def new_function(*args, **kwargs):
    res = f(*args, **kwargs)
    request = args[0]
    with_full = False
    if request.GET.get('full') == '1':
      with_full = True
    return obj_to_dict(res, with_full)
  return new_function

def model_to_json(f):
  """Decorator that combines py_to_json and model_to_py."""
  @py_to_json
  @model_to_py
  def new_function(*args, **kwargs):
    return f(*args, **kwargs)
  return new_function

### Helpers

def _get_last_drinks(request, limit=5):
  return request.kbsite.drinks.valid()[:limit]

### Endpoints

@model_to_json
def last_drinks(request, limit=5):
  return _get_last_drinks(request, limit)

@model_to_json
def all_kegs(request):
  return request.kbsite.keg_set.all().order_by('-startdate')

@model_to_json
@auth_required   # for now, due to expense; TODO paginate me
def all_drinks(request):
  return models.Drink.objects.all().order_by('id')

@model_to_json
def get_drink(request, drink_id):
  return get_object_or_404(models.Drink, pk=drink_id, site=request.kbsite)

@model_to_json
def get_keg(request, keg_id):
  return get_object_or_404(models.Keg, pk=keg_id, site=request.kbsite)

@model_to_json
def get_keg_drinks(request, keg_id):
  keg = get_object_or_404(models.Keg, pk=keg_id, site=request.kbsite)
  return list(keg.drinks.valid())

@model_to_json
def all_taps(request):
  return request.kbsite.kegtap_set.all().order_by('name')

@model_to_json
def get_user(request, username):
  return get_object_or_404(models.User, username=username)

@model_to_json
def get_user_drinks(request, username):
  user = get_object_or_404(models.User, username=username)
  return list(user.drinks.valid())

@model_to_json
def get_auth_token(request, auth_device, token_value):
  return get_object_or_404(models.AuthenticationToken, auth_device=auth_device,
      token_value=token_value)

@model_to_json
def all_thermo_sensors(request):
  return list(request.kbsite.thermosensors.all())

def _get_sensor_or_404(request, sensor_name):
  try:
    sensor = models.ThermoSensor.objects.get(site=request.kbsite,
        raw_name=sensor_name)
  except models.ThermoSensor.DoesNotExist:
    try:
      sensor = models.ThermoSensor.objects.get(site=request.kbsite,
          nice_name=sensor_name)
    except models.ThermoSensor.DoesNotExist:
      raise Http404
  return sensor

def get_thermo_sensor(request, sensor_name):
  if request.method == 'POST':
    return thermo_sensor_post(request, sensor_name)
  else:
    return thermo_sensor_get(request, sensor_name)

@model_to_json
def thermo_sensor_get(request, sensor_name):
  sensor = _get_sensor_or_404(request, sensor_name)
  return sensor

@py_to_json
@auth_required
def thermo_sensor_post(request, sensor_name):
  sensor = _get_sensor_or_404(request, sensor_name)
  form = forms.ThermoPostForm(request.POST)
  if not form.is_valid():
    raise common.BadRequestError
  cd = form.cleaned_data
  b = backend.KegbotBackend(site=request.kbsite)
  # TODO(mikey): use form fields to compute `when`
  res = b.LogSensorReading(sensor.raw_name, cd['temp_c'])
  return protoutil.ProtoMessageToDict(res)

@model_to_json
def get_thermo_sensor_logs(request, sensor_name):
  sensor = _get_sensor_or_404(request, sensor_name)
  logs = sensor.thermolog_set.all()[:60*2]
  return logs

@py_to_json
def last_drinks_html(request, limit=5):
  last_drinks = _get_last_drinks(request, limit)

  # render each drink
  template = get_template('kegweb/drink-box.html')
  results = []
  for d in last_drinks:
    row = {}
    row['id'] = d.id
    row['box_html'] = template.render(Context({'drink': d}))
    results.append(row)
  return results

@py_to_json
def last_drink_id(request):
  last = _get_last_drinks(request, limit=1)
  if not last.count():
    return {'id': 0}
  else:
    return {'id': last[0].id}

@py_to_json
@staff_member_required
def get_access_token(request):
  return {'token': AUTH_KEY}

def tap_detail(request, tap_id):
  if request.method == 'POST':
    return tap_detail_post(request, tap_id)
  else:
    return tap_detail_get(request, tap_id)

@model_to_json
def tap_detail_get(request, tap_id):
  return get_object_or_404(models.KegTap, meter_name=tap_id, site=request.kbsite)

@py_to_json
@auth_required
def tap_detail_post(request, tap):
  form = forms.DrinkPostForm(request.POST)
  if not form.is_valid():
    raise common.BadRequestError
  cd = form.cleaned_data
  if cd.get('pour_time') and cd.get('now'):
    pour_time = datetime.datetime.fromtimestamp(cd.get('pour_time'))
    now = datetime.datetime.fromtimestamp(cd.get('now'))
    skew = datetime.datetime.now() - now
    pour_time += skew
  else:
    pour_time = None
  b = backend.KegbotBackend(site=request.kbsite)
  res = b.RecordDrink(tap_name=tap.meter_name,
    ticks=cd['ticks'],
    volume_ml=cd.get('volume_ml'),
    username=cd.get('username'),
    pour_time=pour_time,
    duration=cd.get('duration'),
    auth_token=cd.get('auth_token'))
  return protoutil.ProtoMessageToDict(res)

@py_to_json
def default_handler(request):
  raise Http404, "Not an API endpoint: %s" % request.path[:100]
