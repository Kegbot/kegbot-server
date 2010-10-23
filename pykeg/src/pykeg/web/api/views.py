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

import datetime
from functools import wraps
import hashlib
import sys
from decimal import Decimal

from django.conf import settings
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import Context
from django.template.loader import get_template

from pykeg.core import backend
from pykeg.core import kbjson
from pykeg.core import models
from pykeg.core import protolib
from pykeg.web.api import krest
from pykeg.web.api import forms

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
      raise krest.NoAuthTokenError
    if tok.lower() == AUTH_KEY.lower():
      return viewfunc(request, *args, **kwargs)
    else:
      raise krest.BadAuthTokenError
  return wraps(viewfunc)(_check_token)

def staff_required(viewfunc):
  def _check_token(request, *args, **kwargs):
    if not request.user or not request.user.is_staff or not \
        request.user.is_superuser:
      raise krest.PermissionDeniedError, "Logged-in staff user required"
    return viewfunc(request, *args, **kwargs)
  return wraps(viewfunc)(_check_token)

def ToJsonError(e):
  """Converts an exception to an API error response."""
  http_code = 500
  if isinstance(e, krest.Error):
    code = e.__class__.__name__
    message = e.Message()
    http_code = e.HTTP_CODE
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
  return result, http_code

def obj_to_dict(o):
  if hasattr(o, '__iter__'):
    return [protolib.ToProto(x) for x in o]
  else:
    return protolib.ToProto(o)

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
    http_code = 200
    try:
      try:
        result = {'result' : f(*args, **kwargs)}
      except Http404, e:
        # We might change the HTTP status code here one day.  This also allows
        # the views to use Http404 (rather than NotFound).
        raise krest.NotFoundError(e.message)
      data = kbjson.dumps(result)
    except Exception, e:
      request = args[0]
      if 'deb' in request.GET:
        raise
      result, http_code = ToJsonError(e)
      data = kbjson.dumps(result)
    return HttpResponse(data, mimetype='application/json', status=http_code)
  return new_function

### Helpers

def _get_last_drinks(request, limit=5):
  return request.kbsite.drinks.valid()[:limit]

def _form_errors(form):
  ret = {}
  for field in form:
    if field.errors:
      name = field.html_name
      ret[name] = []
      for error in field.errors:
        ret[name].append(error)
  return ret

### Endpoints

@py_to_json
def last_drinks(request, limit=5):
  drinks = _get_last_drinks(request, limit)
  res = {
    'drinks': obj_to_dict(drinks),
  }
  return res

@py_to_json
def all_kegs(request):
  kegs = request.kbsite.kegs.all().order_by('-startdate')
  res = {
    'kegs': obj_to_dict(kegs),
  }
  return res

@py_to_json
def all_drinks(request, limit=100):
  qs = request.kbsite.drinks.all()
  total = len(qs)
  if 'start' in request.GET:
    try:
      start = int(request.GET['start'])
      qs = qs.filter(seqn__lte=start)
    except ValueError:
      pass
  qs = qs.order_by('-seqn')
  qs = qs[:limit]
  start = qs[0].seqn
  count = len(qs)
  res = {
    'drinks' : obj_to_dict(qs),
  }
  if count < total:
    res['paging'] = {
      'pos': start,
      'total': total,
      'limit': limit,
    }
  return res

@py_to_json
def get_drink(request, drink_id):
  drink = get_object_or_404(models.Drink, pk=drink_id, site=request.kbsite)
  res = {
    'drink': obj_to_dict(drink),
    'user': obj_to_dict(drink.user),
    'keg': obj_to_dict(drink.keg),
    'session': obj_to_dict(drink.session),
  }
  return res

@py_to_json
def get_keg(request, keg_id):
  keg = get_object_or_404(models.Keg, pk=keg_id, site=request.kbsite)
  res = {
    'keg': obj_to_dict(keg),
    'type': obj_to_dict(keg.type),
    'size': obj_to_dict(keg.size),
    'drinks': obj_to_dict(keg.drinks.valid()),
    # TODO(mikey): add sessions
  }
  return res

@py_to_json
def get_keg_drinks(request, keg_id):
  keg = get_object_or_404(models.Keg, pk=keg_id, site=request.kbsite)
  res = {
    'drinks': obj_to_dict(keg.drinks.valid()),
  }
  return res

@py_to_json
def get_keg_sessions(request, keg_id):
  keg = get_object_or_404(models.Keg, pk=keg_id, site=request.kbsite)
  sessions = [c.session for c in keg.keg_session_chunks.all()]
  res = {
    'sessions': obj_to_dict(sessions),
  }
  return res

@py_to_json
def all_taps(request):
  taps = request.kbsite.kegtap_set.all().order_by('name')
  tap_list = []
  for tap in taps:
    beer_type = None
    tap_entry = {
      'tap': obj_to_dict(tap),
      'keg': obj_to_dict(tap.current_keg),
    }
    if tap.current_keg and tap.current_keg.type:
      tap_entry['beverage'] = obj_to_dict(tap.current_keg.type)
    else:
      tap_entry['beverage'] = None
    tap_list.append(tap_entry)
  res = {'taps': tap_list}
  return res

@py_to_json
def get_user(request, username):
  user = get_object_or_404(models.User, username=username)
  res = {
    'user': obj_to_dict(user),
  }
  return res

@py_to_json
def get_user_drinks(request, username):
  user = get_object_or_404(models.User, username=username)
  drinks = user.drinks.valid()
  res = {
    'drinks': obj_to_dict(drinks),
  }
  return res

@py_to_json
def get_user_stats(request, username):
  user = get_object_or_404(models.User, username=username)
  stats = user.get_profile().GetStats()
  res = {
    'stats': stats,
  }
  return res

@py_to_json
@auth_required
def get_auth_token(request, auth_device, token_value):
  token = get_object_or_404(models.AuthenticationToken, auth_device=auth_device,
      token_value=token_value)
  res = {
    'token': obj_to_dict(token),
  }
  return res

@py_to_json
def all_thermo_sensors(request):
  sensors = list(request.kbsite.thermosensors.all())
  res = {
    'sensors': obj_to_dict(sensors),
  }
  return res

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

@py_to_json
def thermo_sensor_get(request, sensor_name):
  sensor = _get_sensor_or_404(request, sensor_name)
  logs = sensor.thermolog_set.all()
  if not logs:
    last_temp = None
    last_time = None
  else:
    last_temp = logs[0].temp
    last_time = logs[0].time
  res = {
    'sensor': obj_to_dict(sensor),
    'last_temp': last_temp,
    'last_time': last_time,
  }
  return res

@py_to_json
@auth_required
def thermo_sensor_post(request, sensor_name):
  sensor = _get_sensor_or_404(request, sensor_name)
  form = forms.ThermoPostForm(request.POST)
  if not form.is_valid():
    raise krest.BadRequestError, _form_errors(form)
  cd = form.cleaned_data
  b = backend.KegbotBackend(site=request.kbsite)
  # TODO(mikey): use form fields to compute `when`
  return b.LogSensorReading(sensor.raw_name, cd['temp_c'])

@py_to_json
def get_thermo_sensor_logs(request, sensor_name):
  sensor = _get_sensor_or_404(request, sensor_name)
  logs = sensor.thermolog_set.all()[:60*2]
  res = {
    'logs': obj_to_dict(logs),
  }
  return res

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
@staff_required
def get_access_token(request):
  return {'token': AUTH_KEY}

def tap_detail(request, tap_id):
  if request.method == 'POST':
    return tap_detail_post(request, tap_id)
  else:
    return tap_detail_get(request, tap_id)

@py_to_json
def tap_detail_get(request, tap_id):
  tap = get_object_or_404(models.KegTap, meter_name=tap_id, site=request.kbsite)
  tap_entry = {
    'tap': obj_to_dict(tap),
    'keg': obj_to_dict(tap.current_keg),
  }
  return tap_entry

@py_to_json
@auth_required
def tap_detail_post(request, tap):
  form = forms.DrinkPostForm(request.POST)
  if not form.is_valid():
    raise krest.BadRequestError, _form_errors(form)
  cd = form.cleaned_data
  if cd.get('pour_time') and cd.get('now'):
    pour_time = datetime.datetime.fromtimestamp(cd.get('pour_time'))
    now = datetime.datetime.fromtimestamp(cd.get('now'))
    skew = datetime.datetime.now() - now
    pour_time += skew
  else:
    pour_time = None
  b = backend.KegbotBackend(site=request.kbsite)
  try:
    res = b.RecordDrink(tap_name=tap,
      ticks=cd['ticks'],
      volume_ml=cd.get('volume_ml'),
      username=cd.get('username'),
      pour_time=pour_time,
      duration=cd.get('duration'),
      auth_token=cd.get('auth_token'))
    return res
  except backend.BackendError, e:
    raise krest.ServerError(str(e))

@py_to_json
def default_handler(request):
  raise Http404, "Not an API endpoint: %s" % request.path[:100]
