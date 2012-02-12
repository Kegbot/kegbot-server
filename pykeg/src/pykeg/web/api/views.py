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
import logging
import sys
import traceback
from decimal import Decimal

import raven

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

from pykeg.contrib.soundserver import models as soundserver_models
from pykeg.core import backend
from pykeg.core import kbjson
from pykeg.core import models
from pykeg.proto import protolib
from pykeg.proto import protoutil
from pykeg.web.api import apikey
from pykeg.web.api import forms
from pykeg.web.api import krest

_LOGGER = logging.getLogger(__name__)

### Decorators

def check_authorization(request):
  # Admin/staff users are always authorized.
  if request.user.is_staff or request.user.is_superuser:
    return True

  keystr = request.REQUEST.get('api_key')
  if not keystr:
    raise krest.NoAuthTokenError('The parameter "api_key" is required')

  try:
    key = apikey.ApiKey.FromString(keystr)
  except ValueError, e:
    raise krest.BadAuthTokenError('Error parsing API key: %s' % e)

  try:
    user = models.User.objects.get(pk=key.uid())
  except models.User.DoesNotExist:
    raise krest.BadAuthTokenError('API user %s does not exist' % key.uid())

  if not user.is_active:
    raise krest.BadAuthTokenError('User is inactive')

  if not user.is_staff and not user.is_superuser:
    raise krest.PermissionDeniedError('User is not staff/superuser')

  user_secret = user.get_profile().api_secret
  if not user_secret or user_secret != key.secret():
    raise krest.BadAuthTokenError('User secret does not match')

def auth_required(viewfunc):
  def _check_token(request, *args, **kwargs):
    check_authorization(request)
    return viewfunc(request, *args, **kwargs)
  return wraps(viewfunc)(_check_token)

def staff_required(viewfunc):
  def _check_token(request, *args, **kwargs):
    if not request.user or (not request.user.is_staff and not \
        request.user.is_superuser):
      raise krest.PermissionDeniedError, "Logged-in staff user required"
    return viewfunc(request, *args, **kwargs)
  return wraps(viewfunc)(_check_token)

def ToJsonError(e, exc_info):
  """Converts an exception to an API error response."""
  # Wrap some common exception types into Krest types
  if isinstance(e, Http404):
    e = krest.NotFoundError(e.message)
  elif isinstance(e, ValueError):
    e = krest.BadRequestError(str(e))
  elif isinstance(e, backend.NoTokenError):
    e = krest.NotFoundError(e.message)

  # Now determine the response based on the exception type.
  if isinstance(e, krest.Error):
    code = e.__class__.__name__
    http_code = e.HTTP_CODE
    message = e.Message()
  else:
    code = 'ServerError'
    http_code = 500
    message = 'An internal error occurred: %s' % str(e)
    if settings.DEBUG:
      message += "\n" + "\n".join(traceback.format_exception(*exc_info))
      client = LocalRavenClient([])
      client.create_from_exception(exc_info)
  result = {
    'error' : {
      'code' : code,
      'message' : message
    }
  }
  return result, http_code

def obj_to_dict(o):
  return protolib.ToDict(o)

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
    request = args[0]
    http_code = 200
    indent = 2
    if 'indent' in request.GET:
      if request.GET['indent'] == '':
        indent = None
      else:
        try:
          indent_val = int(request.GET['indent'])
          if indent_val >= 0 and indent_val <= 8:
            indent = indent_val
        except ValueError:
          pass
    try:
      result_data = {'result' : f(*args, **kwargs)}
    except Exception, e:
      if settings.DEBUG and 'deb' in request.GET:
        raise
      result_data, http_code = ToJsonError(e, sys.exc_info())
    return HttpResponse(kbjson.dumps(result_data, indent=indent),
        mimetype='application/json', status=http_code)
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

def FromProto(m):
  return protoutil.ProtoMessageToDict(m)

@py_to_json
def last_drinks(request, limit=5):
  drinks = _get_last_drinks(request, limit)
  return FromProto(protolib.GetDrinkSet(drinks))

@py_to_json
def all_kegs(request):
  kegs = request.kbsite.kegs.all().order_by('-startdate')
  return FromProto(protolib.GetKegDetailSet(kegs, full=False))

@py_to_json
def all_drinks(request, limit=100):
  qs = request.kbsite.drinks.valid()
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

  result = protolib.GetDrinkSet(qs)
  if count < total:
    result.paging.pos = start
    result.paging.total = total
    result.paging.limit = limit
  return FromProto(result)

@py_to_json
def get_drink(request, drink_id):
  drink = get_object_or_404(models.Drink, seqn=drink_id, site=request.kbsite)
  return protoutil.ProtoMessageToDict(protolib.GetDrinkDetail(drink))

@csrf_exempt
@py_to_json
@auth_required
def add_drink_photo(request, drink_id):
  if request.method != 'POST':
    raise Http404('Method not supported')
  drink = get_object_or_404(models.Drink, seqn=drink_id, site=request.kbsite)
  pic = models.Picture.objects.create(site=request.kbsite)
  pic.image = request.FILES['photo']
  pic.drink = drink
  pic.user = drink.user
  pic.keg = drink.keg
  pic.session = drink.session
  pic.save()
  return obj_to_dict(pic)

@py_to_json
def get_session(request, session_id):
  session = get_object_or_404(models.DrinkingSession, seqn=session_id,
      site=request.kbsite)
  return protoutil.ProtoMessageToDict(protolib.GetSessionDetail(session))

@py_to_json
def get_session_stats(request, session_id):
  session = get_object_or_404(models.DrinkingSession, seqn=session_id,
      site=request.kbsite)
  stats = session.GetStats()
  return FromProto(stats)

@py_to_json
def get_keg(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  return protoutil.ProtoMessageToDict(protolib.GetKegDetail(keg, full=True))

@py_to_json
def get_keg_drinks(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  drinks = keg.drinks.valid()
  return FromProto(protolib.GetDrinkSet(drinks))

@py_to_json
def get_keg_events(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  events = keg.events.all()
  events = apply_since(request, events)
  return FromProto(protolib.GetSystemEventDetailSet(events))

@py_to_json
def all_sessions(request):
  sessions = request.kbsite.sessions.all()
  return FromProto(protolib.GetSessionSet(sessions))

@py_to_json
def current_sessions(request):
  session_list = []
  try:
    latest = request.kbsite.sessions.latest()
    if latest.IsActiveNow():
      session_list.append(latest)
  except models.DrinkingSession.DoesNotExist:
    pass
  return FromProto(protolib.GetSessionSet(session_list))

@py_to_json
def all_events(request):
  events = request.kbsite.events.all().order_by('-seqn')
  events = apply_since(request, events)
  events = events[:20]
  return FromProto(protolib.GetSystemEventDetailSet(events))

def apply_since(request, query):
  """Restricts the query to `since` events, if given."""
  since_str = request.GET.get('since')
  if since_str:
    try:
      since = int(since_str)
      return query.filter(seqn__gt=since)
    except (ValueError, TypeError):
      pass
  return query

@py_to_json
@auth_required
def all_sound_events(request):
  events = soundserver_models.SoundEvent.objects.all()
  return FromProto(protolib.GetSoundEventSet(events))

@py_to_json
def recent_events_html(request):
  events = request.kbsite.events.all().order_by('-seqn')
  events = apply_since(request, events)
  events = events[:20]

  template = get_template('kegweb/event-box.html')
  results = []
  for event in events:
    ctx = RequestContext(request, {
      'event': event,
      'kbsite': request.kbsite,
    })
    row = {}
    row['id'] = str(event.seqn)
    row['html'] = template.render(ctx)
    results.append(row)
  results.reverse()

  return FromProto(protolib.GetSystemEventHtmlSet(results))

@py_to_json
def get_keg_sessions(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  sessions = [c.session for c in keg.keg_session_chunks.all()]
  return FromProto(protolib.GetSessionSet(sessions))

@py_to_json
def get_keg_stats(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  stats = keg.GetStats()
  return FromProto(stats)

@py_to_json
def get_system_stats(request):
  stats = request.kbsite.GetStats()
  return FromProto(stats)

@py_to_json
def all_taps(request):
  taps = request.kbsite.taps.all().order_by('name')
  return FromProto(protolib.GetTapDetailSet(taps))

@py_to_json
@auth_required
def user_list(request):
  users = models.User.objects.filter(is_active=True).order_by('username')
  return FromProto(protolib.GetUserDetailSet(users, full=True))

@py_to_json
def get_user(request, username):
  user = get_object_or_404(models.User, username=username)
  return FromProto(protolib.GetUserDetail(user, full=True))

@py_to_json
def get_user_drinks(request, username):
  user = get_object_or_404(models.User, username=username)
  drinks = user.drinks.valid()
  return FromProto(protolib.GetDrinkSet(drinks))

@py_to_json
def get_user_events(request, username):
  user = get_object_or_404(models.User, username=username)
  return FromProto(protolib.GetSystemEventDetailSet(user.events.all()))

@py_to_json
def get_user_stats(request, username):
  user = get_object_or_404(models.User, username=username)
  # TODO(mikey_) fix stats
  stats = user.get_profile().GetStats()
  res = {
    'stats': FromProto(stats),
  }
  return res

@py_to_json
@auth_required
def get_auth_token(request, auth_device, token_value):
  b = backend.KegbotBackend(site=request.kbsite)
  tok = b.GetAuthToken(auth_device, token_value)
  return FromProto(tok)

@py_to_json
def all_thermo_sensors(request):
  sensors = list(request.kbsite.thermosensors.all())
  return FromProto(protolib.GetThermoSensorSet(sensors))

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

@csrf_exempt
def get_thermo_sensor(request, sensor_name):
  if request.method == 'POST':
    return _thermo_sensor_post(request, sensor_name)
  else:
    return _thermo_sensor_get(request, sensor_name)

@py_to_json
def _thermo_sensor_get(request, sensor_name):
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
def _thermo_sensor_post(request, sensor_name):
  form = forms.ThermoPostForm(request.POST)
  if not form.is_valid():
    raise krest.BadRequestError, _form_errors(form)
  cd = form.cleaned_data
  b = backend.KegbotBackend(site=request.kbsite)
  sensor, created = models.ThermoSensor.objects.get_or_create(site=request.kbsite,
      raw_name=sensor_name)
  # TODO(mikey): use form fields to compute `when`
  return FromProto(b.LogSensorReading(sensor.raw_name, cd['temp_c']))

@py_to_json
def get_thermo_sensor_logs(request, sensor_name):
  sensor = _get_sensor_or_404(request, sensor_name)
  logs = sensor.thermolog_set.all()[:60*2]
  return FromProto(protolib.GetThermoLogSet(logs))

@py_to_json
def last_drinks_html(request, limit=5):
  last_drinks = _get_last_drinks(request, limit)

  # render each drink
  template = get_template('kegweb/drink-box.html')
  results = []
  for d in last_drinks:
    row = {}
    row['id'] = d.id
    row['box_html'] = template.render(RequestContext(request, {'drink': d}))
    results.append(row)
  return results

@py_to_json
def last_drink_id(request):
  last_id = 0
  last = _get_last_drinks(request, limit=1)
  if last.count():
    last_id = last[0].seqn
  return {'id': str(last_id)}

@py_to_json
def get_api_key(request):
  user = request.user
  api_key = ''
  if user and (user.is_staff or user.is_superuser):
    api_key = str(user.get_profile().GetApiKey())
  return {'api_key': api_key}

@csrf_exempt
def tap_detail(request, tap_id):
  if request.method == 'POST':
    return _tap_detail_post(request, tap_id)
  else:
    return _tap_detail_get(request, tap_id)

@py_to_json
def _tap_detail_get(request, tap_id):
  tap = get_object_or_404(models.KegTap, meter_name=tap_id, site=request.kbsite)
  return protoutil.ProtoMessageToDict(protolib.GetTapDetail(tap))

@py_to_json
@auth_required
def _tap_detail_post(request, tap):
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
  duration = cd.get('duration')
  if duration is None:
    duration = 0
  b = backend.KegbotBackend(site=request.kbsite)
  try:
    res = b.RecordDrink(tap_name=tap,
      ticks=cd['ticks'],
      volume_ml=cd.get('volume_ml'),
      username=cd.get('username'),
      pour_time=pour_time,
      duration=duration,
      auth_token=cd.get('auth_token'),
      spilled=cd.get('spilled'))
    return FromProto(res)
  except backend.BackendError, e:
    raise krest.ServerError(str(e))

@csrf_exempt
@py_to_json
@auth_required
def cancel_drink(request):
  #if request.method != 'POST':
  #  raise krest.BadRequestError, 'Method not supported at this endpoint'
  #form = forms.DrinkCancelForm(request.POST)
  form = forms.CancelDrinkForm(request.GET)
  if not form.is_valid():
    raise krest.BadRequestError, _form_errors(form)
  cd = form.cleaned_data
  b = backend.KegbotBackend(site=request.kbsite)
  try:
    res = b.CancelDrink(seqn=cd.get('id'), spilled=cd.get('spilled', False))
    return FromProto(res)
  except backend.BackendError, e:
    raise krest.ServerError(str(e))

@csrf_exempt
@py_to_json
def login(request):
  if request.POST:
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
      auth_login(request, form.get_user())
      if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
      return {'result': 'ok'}
    else:
      raise krest.PermissionDeniedError('Login failed.')
  raise krest.BadRequestError('POST required.')

@py_to_json
def logout(request):
  auth_logout(request)
  return {'result': 'ok'}

@py_to_json
def default_handler(request):
  raise Http404, "Not an API endpoint: %s" % request.path[:100]


class LocalRavenClient(raven.Client):
  logger = logging.getLogger('kegbot.api.client.debug')
  def send(self, **kwargs):
    from sentry.models import GroupedMessage
    return GroupedMessage.objects.from_kwargs(**kwargs)

@csrf_exempt
@py_to_json
@auth_required
def debug_log(request):
  if request.method != 'POST':
    raise Http404('Method not supported')
  form = forms.DebugLogForm(request.POST)
  if not form.is_valid():
    raise krest.BadRequestError(_form_errors(form))
  client = LocalRavenClient([])
  message = form.cleaned_data['message']
  ident = client.get_ident(client.create_from_text(message))
  client.send()
  return {'log_id': ident}

