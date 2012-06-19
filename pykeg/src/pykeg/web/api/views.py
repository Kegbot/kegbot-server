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
import types

from google.protobuf.message import Message

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.utils import IntegrityError

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.db.models.query import QuerySet

from pykeg.contrib.soundserver import models as soundserver_models
from pykeg.core.backend import backend
from pykeg.core.backend.django import KegbotBackend
from pykeg.core import kbjson
from pykeg.core import models
from pykeg.proto import protolib
from pykeg.proto import protoutil
from pykeg.web.api import apikey
from pykeg.web.api import forms
from pykeg.web.api import krest

if settings.HAVE_CELERY:
  from pykeg.web import tasks

if settings.HAVE_RAVEN:
  import raven

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
    raise krest.BadApiKeyError('Error parsing API key: %s' % e)

  try:
    user = models.User.objects.get(pk=key.uid())
  except models.User.DoesNotExist:
    raise krest.BadApiKeyError('API user %s does not exist' % key.uid())

  if not user.is_active:
    raise krest.BadApiKeyError('User is inactive')

  if not user.is_staff and not user.is_superuser:
    raise krest.PermissionDeniedError('User is not staff/superuser')

  user_secret = user.get_profile().api_secret
  if not user_secret or user_secret != key.secret():
    raise krest.BadApiKeyError('User secret does not match')

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
  if settings.DEBUG and settings.HAVE_RAVEN:
    from raven.contrib.django.models import client
    client.captureException()
  result = {
    'error' : {
      'code' : code,
      'message' : message
    }
  }
  return result, http_code

def py_to_json(f):
  """Decorator that wraps an API method.

  The decorator transforms the method in a few ways:
    - The raw return value from the method is converted to a serialized JSON
      result.
    - The result is wrapped in an outer dict, and set as the value 'result'
    - If an exception is thrown during the method, it is converted to a protocol
      error message.
  """
  @never_cache
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
      result_data = prepare_data(f(*args, **kwargs))
      result_data['meta'] = {
        'result': 'ok'
      }
    except Exception, e:
      exc_info = sys.exc_info()
      if settings.DEBUG and 'deb' in request.GET:
        raise exc_info[1], None, exc_info[2]
      result_data, http_code = ToJsonError(e, exc_info)
      result_data['meta'] = {
        'result': 'error'
      }
    return HttpResponse(kbjson.dumps(result_data, indent=indent),
        mimetype='application/json', status=http_code)
  return wraps(f)(new_function)

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

### Helpers

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
def all_kegs(request):
  return request.kbsite.kegs.all().order_by('-start_time')

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
  return qs

@py_to_json
def get_drink(request, drink_id):
  drink = get_object_or_404(models.Drink, seqn=drink_id, site=request.kbsite)
  return protolib.ToProto(drink, full=True)

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
  if settings.HAVE_CELERY:
    tasks.handle_new_picture.delay(pic.id)
  return protolib.ToProto(pic, full=True)

@py_to_json
def get_session(request, session_id):
  session = get_object_or_404(models.DrinkingSession, seqn=session_id,
      site=request.kbsite)
  return protolib.ToProto(session, full=True)

@py_to_json
def get_session_stats(request, session_id):
  session = get_object_or_404(models.DrinkingSession, seqn=session_id,
      site=request.kbsite)
  return session.GetStats()

@py_to_json
def get_keg(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  return protolib.ToProto(keg, full=True)

@py_to_json
def get_keg_drinks(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  return keg.drinks.valid()

@py_to_json
def get_keg_events(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  events = keg.events.all()
  events = apply_since(request, events)
  return events

@py_to_json
def all_sessions(request):
  return request.kbsite.sessions.all()

@py_to_json
def current_session(request):
  current = None
  try:
    latest = request.kbsite.sessions.latest()
    if latest.IsActiveNow():
      return latest
  except models.DrinkingSession.DoesNotExist:
    raise Http404

@py_to_json
def all_events(request):
  events = request.kbsite.events.all().order_by('-seqn')
  events = apply_since(request, events)
  events = events[:10]
  return [protolib.ToProto(e, full=True) for e in events]

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
  return soundserver_models.SoundEvent.objects.all()

@py_to_json
def get_keg_sessions(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  sessions = [c.session for c in keg.keg_session_chunks.all()]
  return sessions

@py_to_json
def get_keg_stats(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  return keg.GetStatsRecord()

@py_to_json
def get_system_stats(request):
  return request.kbsite.GetStatsRecord()

@py_to_json
def all_taps(request):
  return request.kbsite.taps.all().order_by('name')

@py_to_json
@auth_required
def user_list(request):
  return models.User.objects.filter(is_active=True).order_by('username')

@py_to_json
def get_user(request, username):
  user = get_object_or_404(models.User, username=username)
  return protolib.ToProto(user, full=True)

@py_to_json
def get_user_drinks(request, username):
  user = get_object_or_404(models.User, username=username)
  return user.drinks.valid()

@py_to_json
def get_user_events(request, username):
  user = get_object_or_404(models.User, username=username)
  return user.events.all()

@py_to_json
def get_user_stats(request, username):
  user = get_object_or_404(models.User, username=username)
  return user.get_profile().GetStatsRecord()

@py_to_json
@auth_required
def get_auth_token(request, auth_device, token_value):
  b = KegbotBackend(site=request.kbsite)
  tok = b.GetAuthToken(auth_device, token_value)
  return tok

@py_to_json
def all_thermo_sensors(request):
  return request.kbsite.thermosensors.all()

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
    'sensor': to_dict(sensor),
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
  b = KegbotBackend(site=request.kbsite)
  sensor, created = models.ThermoSensor.objects.get_or_create(site=request.kbsite,
      raw_name=sensor_name)
  # TODO(mikey): use form fields to compute `when`
  return b.LogSensorReading(sensor.raw_name, cd['temp_c'])

@py_to_json
def get_thermo_sensor_logs(request, sensor_name):
  sensor = _get_sensor_or_404(request, sensor_name)
  return sensor.thermolog_set.all()[:60*2]

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
  return protolib.ToProto(tap, full=True)

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
  b = KegbotBackend(site=request.kbsite)
  try:
    res = b.RecordDrink(tap_name=tap,
      ticks=cd['ticks'],
      volume_ml=cd.get('volume_ml'),
      username=cd.get('username'),
      pour_time=pour_time,
      duration=duration,
      auth_token=cd.get('auth_token'),
      spilled=cd.get('spilled'),
      shout=cd.get('shout'))
    return protolib.ToProto(res, full=True)
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
  b = KegbotBackend(site=request.kbsite)
  try:
    res = b.CancelDrink(seqn=cd.get('id'), spilled=cd.get('spilled', False))
    return protolib.ToProto(res, full=True)
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

@csrf_exempt
@py_to_json
@auth_required
def register(request):
  if not request.POST:
    raise krest.BadRequestError('POST required.')
  form = forms.RegisterForm(request.POST)
  errors = {}
  if not form.is_valid():
    errors = _form_errors(form)
  else:
    username = form.cleaned_data['username']
    try:
      u = models.User()
      u.username = username
      u.email = form.cleaned_data['email']
      u.save()
      u.set_password(form.cleaned_data['password'])
      if 'photo' in request.FILES:
        pic = models.Picture.objects.create(user=u)
        photo = request.FILES['photo']
        pic.image.save(photo.name, photo)
        pic.save()
        profile = u.get_profile()
        profile.mugshot = pic
        profile.save()
      return protolib.ToProto(u, full=True)
    except IntegrityError:
      user_errs = errors.get('username', [])
      user_errs.append('Username not available.')
      errors['username'] = user_errs
  raise krest.BadRequestError(errors)

@py_to_json
def default_handler(request):
  raise Http404, "Not an API endpoint: %s" % request.path[:100]

if settings.HAVE_RAVEN and settings.HAVE_SENTRY:
  class LocalRavenClient(raven.Client):
    logger = logging.getLogger('kegbot.api.client.debug')
    def send(self, **kwargs):
      from sentry.models import GroupedMessage
      return GroupedMessage.objects.from_kwargs(**kwargs)

@csrf_exempt
@py_to_json
@auth_required
def debug_log(request):
  if request.method != 'POST' or not settings.HAVE_RAVEN or not settings.HAVE_SENTRY:
    raise Http404('Method not supported')

  form = forms.DebugLogForm(request.POST)
  if not form.is_valid():
    raise krest.BadRequestError(_form_errors(form))
  client = LocalRavenClient([])
  message = form.cleaned_data['message']
  ident = client.get_ident(client.create_from_text(message))
  client.send()
  return {'log_id': ident}

