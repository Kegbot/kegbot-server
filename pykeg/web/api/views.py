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
import logging
from functools import wraps

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.utils import IntegrityError
from django.utils import timezone

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from kegbot.api import kbapi

from pykeg.contrib.soundserver import models as soundserver_models
from pykeg.core import backend
from pykeg.core import models
from pykeg.proto import protolib
from pykeg.web.api import forms
from pykeg.web.api import util
from pykeg.web.kegadmin.forms import ChangeKegForm

from pykeg.web import tasks

_LOGGER = logging.getLogger(__name__)

### Decorators

def auth_required(view_func):
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    util.set_needs_auth(wrapped_view)
    return wraps(view_func)(wrapped_view)

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

def all_kegs(request):
    return models.Keg.objects.all().order_by('-start_time')

def all_drinks(request, limit=100):
    qs = models.Drink.objects.all()
    if 'start' in request.GET:
        try:
            start = int(request.GET['start'])
            qs = qs.filter(id__lte=start)
        except ValueError:
            pass
    qs = qs.order_by('-id')
    qs = qs[:limit]
    start = qs[0].id
    return qs

def get_drink(request, drink_id):
    drink = get_object_or_404(models.Drink, id=drink_id)
    return protolib.ToProto(drink, full=True)

@csrf_exempt
@auth_required
def add_drink_photo(request, drink_id):
    if request.method != 'POST':
        raise Http404('Method not supported')
    drink = get_object_or_404(models.Drink, id=drink_id)
    pic = models.Picture.objects.create(image=request.FILES['photo'])
    pour_pic = models.PourPicture.objects.create(picture_id=pic.id,
        drink=drink,
        user=drink.user,
        keg=drink.keg,
        session=drink.session)
    tasks.handle_new_picture.delay(pour_pic.id)
    return protolib.ToProto(pour_pic, full=True)

def get_session(request, session_id):
    session = get_object_or_404(models.DrinkingSession, id=session_id)
    return protolib.ToProto(session, full=True)

def get_session_stats(request, session_id):
    session = get_object_or_404(models.DrinkingSession, id=session_id)
    return session.GetStats()

def get_keg(request, keg_id):
    keg = get_object_or_404(models.Keg, id=keg_id)
    return protolib.ToProto(keg, full=True)

def get_keg_drinks(request, keg_id):
    keg = get_object_or_404(models.Keg, id=keg_id)
    return keg.drinks.all()

def get_keg_events(request, keg_id):
    keg = get_object_or_404(models.Keg, id=keg_id)
    events = keg.events.all()
    events = apply_since(request, events)
    return events

def get_keg_sizes(request):
    return models.KegSize.objects.all()

@require_http_methods(["POST"])
@auth_required
@csrf_exempt
def end_keg(request, keg_id):
    keg = get_object_or_404(models.Keg, id=keg_id)
    tap = keg.current_tap
    keg = request.backend.EndKeg(tap)
    return protolib.ToProto(keg, full=True)

def all_sessions(request):
    return models.DrinkingSession.objects.all()

def current_session(request):
    try:
        latest = models.DrinkingSession.objects.latest()
        if latest.IsActiveNow():
            return latest
    except models.DrinkingSession.DoesNotExist:
        raise Http404

def all_events(request):
    events = models.SystemEvent.objects.all().order_by('-id')
    events = apply_since(request, events)
    events = events[:10]
    return [protolib.ToProto(e, full=True) for e in events]

def apply_since(request, query):
    """Restricts the query to `since` events, if given."""
    since_str = request.GET.get('since')
    if since_str:
        try:
            since = int(since_str)
            return query.filter(id__gt=since)
        except (ValueError, TypeError):
            pass
    return query

@auth_required
def all_sound_events(request):
    return soundserver_models.SoundEvent.objects.all()

def get_keg_sessions(request, keg_id):
    keg = get_object_or_404(models.Keg, id=keg_id)
    sessions = [c.session for c in keg.keg_session_chunks.all()]
    return sessions

def get_keg_stats(request, keg_id):
    keg = get_object_or_404(models.Keg, id=keg_id)
    return keg.GetStats()

def get_system_stats(request):
    return models.KegbotSite.get().GetStats()

def all_taps(request):
    return models.KegTap.objects.all().order_by('name')

@auth_required
def user_list(request):
    return models.User.objects.filter(is_active=True).order_by('username')

def get_user(request, username):
    user = get_object_or_404(models.User, username=username)
    return protolib.ToProto(user, full=True)

def get_user_drinks(request, username):
    user = get_object_or_404(models.User, username=username)
    return user.drinks.all()

def get_user_events(request, username):
    user = get_object_or_404(models.User, username=username)
    return user.events.all()

def get_user_stats(request, username):
    user = get_object_or_404(models.User, username=username)
    return user.get_profile().GetStats()

@auth_required
def get_auth_token(request, auth_device, token_value):
    tok = request.backend.GetAuthToken(auth_device, token_value)
    return tok

@csrf_exempt
@auth_required
def assign_auth_token(request, auth_device, token_value):
    if not request.POST:
        raise kbapi.BadRequestError('POST required.')

    form = forms.AssignTokenForm(request.POST)
    if not form.is_valid():
        errors = _form_errors(form)
        raise kbapi.BadRequestError(errors)

    b = request.backend
    username = form.cleaned_data['username']

    user = backend.get_user(username)
    if not user:
        raise kbapi.BadRequestError("User does not exist")

    try:
        tok = b.GetAuthToken(auth_device, token_value)
    except backend.NoTokenError:
        tok = b.CreateAuthToken(auth_device, token_value, username=username)

    if tok.user != user:
        if tok.user:
            raise kbapi.BadRequestError("Token is already bound to a user")
        tok.user = user
        tok.save()
    return tok

def all_thermo_sensors(request):
    return models.ThermoSensor.objects.all()

def _get_sensor_or_404(request, sensor_name):
    try:
        sensor = models.ThermoSensor.objects.get(raw_name=sensor_name)
    except models.ThermoSensor.DoesNotExist:
        try:
            sensor = models.ThermoSensor.objects.get(nice_name=sensor_name)
        except models.ThermoSensor.DoesNotExist:
            raise Http404
    return sensor

@csrf_exempt
def get_thermo_sensor(request, sensor_name):
    if request.method == 'POST':
        return _thermo_sensor_post(request, sensor_name)
    else:
        return _thermo_sensor_get(request, sensor_name)

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
      'sensor': sensor,
      'last_temp': last_temp,
      'last_time': last_time,
    }
    return res

@auth_required
def _thermo_sensor_post(request, sensor_name):
    form = forms.ThermoPostForm(request.POST)
    if not form.is_valid():
        raise kbapi.BadRequestError, _form_errors(form)
    cd = form.cleaned_data
    sensor, created = models.ThermoSensor.objects.get_or_create(raw_name=sensor_name)
    # TODO(mikey): use form fields to compute `when`
    return request.backend.LogSensorReading(sensor.raw_name, cd['temp_c'])

def get_thermo_sensor_logs(request, sensor_name):
    sensor = _get_sensor_or_404(request, sensor_name)
    return sensor.thermolog_set.all()[:60*2]

def get_api_key(request):
    user = request.user
    api_key = ''
    if user and (user.is_staff or user.is_superuser):
        api_key = user.get_profile().GetApiKey()
    return {'api_key': api_key}

@csrf_exempt
def tap_detail(request, tap_id):
    tap = get_object_or_404(models.KegTap, meter_name=tap_id)
    if request.method == 'POST':
        return _tap_detail_post(request, tap)
    elif request.method == 'GET':
        return _tap_detail_get(request, tap)
    else:
        raise kbapi.BadRequestError('Method not supported')

def _tap_detail_get(request, tap):
    return protolib.ToProto(tap, full=True)

@csrf_exempt
@auth_required
def tap_calibrate(request, tap_id):
    # TODO(mikey): This would make more semantic sense as PATCH /taps/tap-name/,
    # but Django's support for non-POST verbs is poor (specifically wrt request
    # body/form handling).
    tap = get_object_or_404(models.KegTap, meter_name=tap_id)
    form = forms.CalibrateTapForm(request.POST)
    if form.is_valid():
        tap.ml_per_tick = form.cleaned_data['ml_per_tick']
        tap.save()
    else:
        raise kbapi.BadRequestError, _form_errors(form)
    return protolib.ToProto(tap, full=True)

@csrf_exempt
@auth_required
def tap_spill(request, tap_id):
    tap = get_object_or_404(models.KegTap, meter_name=tap_id)
    if not tap.current_keg:
        raise kbapi.BadRequestError('No keg on tap.')
    form = forms.TapSpillForm(request.POST)
    if form.is_valid():
        tap.current_keg.spilled_ml += form.cleaned_data['volume_ml']
        tap.current_keg.save()
    else:
        raise kbapi.BadRequestError, _form_errors(form)
    return protolib.ToProto(tap, full=True)

@csrf_exempt
@auth_required
def tap_activate(request, tap_id):
    tap = get_object_or_404(models.KegTap, meter_name=tap_id)
    form = ChangeKegForm(request.POST)
    if form.is_valid():
        form.save(tap)
    else:
        raise kbapi.BadRequestError, _form_errors(form)
    return protolib.ToProto(tap, full=True)

@auth_required
def _tap_detail_post(request, tap):
    form = forms.DrinkPostForm(request.POST)
    if not form.is_valid():
        raise kbapi.BadRequestError, _form_errors(form)
    cd = form.cleaned_data
    if cd.get('pour_time') and cd.get('now'):
        pour_time = datetime.datetime.fromtimestamp(cd.get('pour_time'))
        pour_now = datetime.datetime.fromtimestamp(cd.get('now'))
        pour_time_ago = pour_now - pour_time
        pour_time = timezone.now() - pour_time_ago
    else:
        pour_time = None
    duration = cd.get('duration')
    if duration is None:
        duration = 0
    try:
        res = request.backend.RecordDrink(tap_name=tap.meter_name,
          ticks=cd['ticks'],
          volume_ml=cd.get('volume_ml'),
          username=cd.get('username'),
          pour_time=pour_time,
          duration=duration,
          shout=cd.get('shout'),
          tick_time_series=cd.get('tick_time_series'))
        return protolib.ToProto(res, full=True)
    except backend.BackendError, e:
        raise kbapi.ServerError(str(e))

@csrf_exempt
@auth_required
def cancel_drink(request):
    if request.method != 'POST':
        raise kbapi.BadRequestError('POST required')
    form = forms.CancelDrinkForm(request.POST)
    if not form.is_valid():
        raise kbapi.BadRequestError, _form_errors(form)
    cd = form.cleaned_data
    try:
        res = request.backend.CancelDrink(drink_id=cd.get('id'), spilled=cd.get('spilled', False))
        return protolib.ToProto(res, full=True)
    except backend.BackendError, e:
        raise kbapi.ServerError(str(e))

@csrf_exempt
def login(request):
    if request.POST:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return {'result': 'ok'}
        else:
            raise kbapi.PermissionDeniedError('Login failed.')
    raise kbapi.BadRequestError('POST required.')

def logout(request):
    auth_logout(request)
    return {'result': 'ok'}

@csrf_exempt
@auth_required
def register(request):
    if not request.POST:
        raise kbapi.BadRequestError('POST required.')
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
            password = form.cleaned_data.get('password')
            if password:
                u.set_password(password)
            else:
                # Must set password using recovery process.
                u.set_unusable_password()
            u.save()
            if 'photo' in request.FILES:
                pic = models.Picture.objects.create()
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
    raise kbapi.BadRequestError(errors)

@csrf_exempt
@auth_required
def user_photo(request, username):
    user = get_object_or_404(models.User, username=username)
    if request.method == 'POST':
        return post_user_photo(request, user)
    else:
        return get_user_photo(request, user)

def get_user_photo(request, user):
    mugshot = user.get_profile().mugshot
    if not mugshot:
        return {}
    return mugshot

def post_user_photo(request, user):
    photo_file = request.FILES.get('photo')
    if not photo_file:
        raise kbapi.BadRequestError('The file "photo" is required.')

    pic = models.Picture.objects.create()
    pic.image.save(photo_file.name, photo_file)
    pic.save()
    profile = user.get_profile()
    profile.mugshot = pic
    profile.save()
    return protolib.ToProto(pic)


def default_handler(request):
    raise Http404, "Not an API endpoint: %s" % request.path[:100]
