# Copyright 2014 Bevbot LLC, All Rights Reserved
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
from django.utils import timezone

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from kegbot.api import kbapi

from pykeg import backend
from pykeg.core import keg_sizes
from pykeg.core import models
from pykeg.core import util as core_util
from pykeg.proto import protolib
from pykeg.web.api import devicelink
from pykeg.web.api import forms
from pykeg.web.api import util
from pykeg.web.kegadmin.forms import ChangeKegForm
from pykeg.web.kegadmin.forms import ControllerForm
from pykeg.web.kegadmin.forms import FlowToggleForm
from pykeg.web.kegadmin.forms import NewFlowMeterForm
from pykeg.web.kegadmin.forms import UpdateFlowMeterForm

_LOGGER = logging.getLogger(__name__)

RESULT_OK = {'result': 'ok'}

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
    return qs


def get_drink(request, drink_id):
    drink = get_object_or_404(models.Drink, id=drink_id)
    return protolib.ToProto(drink, full=True)


@csrf_exempt
@auth_required
def all_controllers(request):
    if request.method == 'POST':
        form = ControllerForm(request.POST)
        if form.is_valid():
            return form.save()
        else:
            errors = _form_errors(form)
            raise kbapi.BadRequestError(errors)

    return models.Controller.objects.all()


@csrf_exempt
@auth_required
def get_controller(request, controller_id):
    controller = get_object_or_404(models.Controller, id=controller_id)

    if request.method == 'DELETE':
        controller.delete()
        return RESULT_OK

    elif request.method == 'POST':
        form = ControllerForm(request.POST, instance=controller)
        if form.is_valid():
            controller = form.save()
        else:
            errors = _form_errors(form)
            raise kbapi.BadRequestError(errors)

    return protolib.ToProto(controller, full=True)


@csrf_exempt
@auth_required
def all_flow_meters(request):
    if request.method == 'POST':
        form = NewFlowMeterForm(request.POST)
        if form.is_valid():
            return form.save()
        else:
            errors = _form_errors(form)
            raise kbapi.BadRequestError(errors)

    return models.FlowMeter.objects.all()


@csrf_exempt
@auth_required
def get_flow_meter(request, flow_meter_id):
    meter = get_object_or_404(models.FlowMeter, id=flow_meter_id)

    if request.method == 'DELETE':
        meter.delete()
        return RESULT_OK

    elif request.method == 'POST':
        form = UpdateFlowMeterForm(request.POST, instance=meter)
        if form.is_valid():
            meter = form.save()
        else:
            errors = _form_errors(form)
            raise kbapi.BadRequestError(errors)

    return protolib.ToProto(meter, full=True)


@csrf_exempt
@auth_required
def all_flow_toggles(request):
    if request.method == 'POST':
        form = FlowToggleForm(request.POST)
        if form.is_valid():
            return form.save()
        else:
            errors = _form_errors(form)
            raise kbapi.BadRequestError(errors)

    return models.FlowToggle.objects.all()


@csrf_exempt
@auth_required
def get_flow_toggle(request, flow_toggle_id):
    toggle = get_object_or_404(models.FlowToggle, id=flow_toggle_id)

    if request.method == 'DELETE':
        toggle.delete()
        return RESULT_OK

    elif request.method == 'POST':
        form = FlowToggleForm(request.POST, instance=toggle)
        if form.is_valid():
            toggle = form.save()
        else:
            errors = _form_errors(form)
            raise kbapi.BadRequestError(errors)

    return protolib.ToProto(toggle, full=True)


@csrf_exempt
@auth_required
def pictures(request):
    if request.method != 'POST':
        raise Http404('Method not supported')
    pic = models.Picture.objects.create(
        image=request.FILES['photo'],
    )
    return protolib.ToProto(pic, full=True)


@csrf_exempt
@auth_required
def add_drink_photo(request, drink_id):
    if request.method != 'POST':
        raise Http404('Method not supported')
    drink = get_object_or_404(models.Drink, id=drink_id)
    pic = _save_pour_pic(request, drink)
    return protolib.ToProto(pic, full=True)


def _save_pour_pic(request, drink):
    pic = models.Picture.objects.create(
        image=request.FILES['photo'],
        user=drink.user,
        keg=drink.keg,
        session=drink.session
    )
    # TODO(mikey): Should we do anything with a previously-saved
    # picture here?
    drink.picture = pic
    drink.save()
    return pic


def get_session(request, session_id):
    session = get_object_or_404(models.DrinkingSession, id=session_id)
    return protolib.ToProto(session, full=True)


def get_session_stats(request, session_id):
    session = get_object_or_404(models.DrinkingSession, id=session_id)
    return session.get_stats()


@auth_required
def get_status(request):
    try:
        session = current_session(request)
    except Http404:
        session = None

    controllers = models.Controller.objects.all()
    drinks = models.Drink.objects.all()[:5]
    events = models.SystemEvent.objects.all()[:5]
    kegs = models.Keg.objects.all().filter(online=True)
    meters = models.FlowMeter.objects.all()
    sound_events = []   # deprecated
    taps = models.KegTap.objects.all()
    toggles = models.FlowToggle.objects.all()

    current_users = set()
    if session:
        for stat in models.Stats.objects.filter(session=session, user__isnull=False):
            user = stat.user
            if not user.is_guest():
                current_users.add(user)

    title = models.KegbotSite.get().title
    version = core_util.get_version()

    response = protolib.GetSyncResponse(
        active_kegs=kegs, active_session=session, active_users=current_users,
        controllers=controllers, drinks=drinks, events=events, meters=meters,
        site_title=title, server_version=version,
        sound_events=sound_events, taps=taps, toggles=toggles)
    return response


def get_version(request):
    return {'server_version': core_util.get_version()}


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
    # Deprecated endpoint.
    ret = []
    fake_id = 0
    for size_name, volume_ml in keg_sizes.VOLUMES_ML.iteritems():
        ret.append({
            'volume_ml': volume_ml,
            'id': fake_id,
            'description': keg_sizes.DESCRIPTIONS[size_name],
        })
        fake_id += 1
    return ret


@require_http_methods(["POST"])
@auth_required
@csrf_exempt
def end_keg(request, keg_id):
    keg = get_object_or_404(models.Keg, id=keg_id)
    tap = keg.current_tap
    keg = request.backend.end_keg(tap)
    return protolib.ToProto(keg, full=True)


def all_sessions(request):
    return models.DrinkingSession.objects.all()


def current_session(request):
    try:
        latest = models.DrinkingSession.objects.latest()
        if latest.IsActiveNow():
            return latest
    except models.DrinkingSession.DoesNotExist:
        pass

    raise Http404('There is no active session.')


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
    return []  # deprecated


def get_keg_sessions(request, keg_id):
    keg = get_object_or_404(models.Keg, id=keg_id)
    sessions = keg.Sessions()
    return sessions


def get_keg_stats(request, keg_id):
    keg = get_object_or_404(models.Keg, id=keg_id)
    return keg.get_stats()


def get_system_stats(request):
    return models.KegbotSite.get().get_stats()


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def all_taps(request):
    if request.method == 'POST':
        util.check_api_key(request)
        return create_tap(request)
    return models.KegTap.objects.all().order_by('name')


def create_tap(request):
    form = forms.TapCreateForm(request.POST)
    if form.is_valid():
        return request.backend.create_tap(name=form.cleaned_data['name'])
    raise kbapi.BadRequestError(_form_errors(form))


@auth_required
def user_list(request):
    return models.User.objects.filter(is_active=True).exclude(username='guest').order_by('username')


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
    return user.get_stats()


@auth_required
def get_auth_token(request, auth_device, token_value):
    tok = request.backend.get_auth_token(auth_device, token_value)
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

    user = b.get_user(username)
    if not user:
        raise kbapi.BadRequestError("User does not exist")

    try:
        tok = b.get_auth_token(auth_device, token_value)
    except backend.exceptions.NoTokenError:
        tok = b.create_auth_token(auth_device, token_value, username=username)

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
    return request.backend.log_sensor_reading(sensor.raw_name, cd['temp_c'])


def get_thermo_sensor_logs(request, sensor_name):
    sensor = _get_sensor_or_404(request, sensor_name)
    return sensor.thermolog_set.all()[:60 * 2]


def get_api_key(request):
    user = request.user
    api_key = ''
    if user and (user.is_staff or user.is_superuser):
        description = request.GET.get('description', '')
        api_key = models.ApiKey.objects.create(description=description)
        api_key = api_key.key
    return {'api_key': api_key}


@csrf_exempt
def tap_detail(request, meter_name_or_id):
    tap = get_tap_from_meter_name_or_404(meter_name_or_id)
    if request.method == 'POST':
        util.check_api_key(request)
        return _tap_detail_post(request, tap)
    elif request.method == 'GET':
        return _tap_detail_get(request, tap)
    elif request.method == 'DELETE':
        util.check_api_key(request)
        tap.delete()
        return RESULT_OK

    raise kbapi.BadRequestError('Method not supported')


def _tap_detail_get(request, tap):
    return protolib.ToProto(tap, full=True)


@csrf_exempt
@auth_required
def tap_calibrate(request, meter_name_or_id):
    # TODO(mikey): This would make more semantic sense as PATCH /taps/tap-name/,
    # but Django's support for non-POST verbs is poor (specifically wrt request
    # body/form handling).
    tap = get_tap_from_meter_name_or_404(meter_name_or_id)
    meter = tap.current_meter()
    if not meter:
        raise kbapi.BadRequestError('Tap does not have a meter!')

    form = forms.CalibrateTapForm(request.POST)
    if form.is_valid():
        meter.ticks_per_ml = 1.0 / form.cleaned_data['ml_per_tick']
        meter.save()
        tap = get_tap_from_meter_name_or_404(meter_name_or_id)
    else:
        raise kbapi.BadRequestError, _form_errors(form)
    return protolib.ToProto(tap, full=True)


@csrf_exempt
@auth_required
def tap_spill(request, meter_name_or_id):
    tap = get_tap_from_meter_name_or_404(meter_name_or_id)
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
def tap_activate(request, meter_name_or_id):
    tap = get_tap_from_meter_name_or_404(meter_name_or_id)
    form = ChangeKegForm(request.POST)
    if form.is_valid():
        form.save(tap)
    else:
        raise kbapi.BadRequestError, _form_errors(form)
    return protolib.ToProto(tap, full=True)


@require_http_methods(["POST"])
@csrf_exempt
@auth_required
def tap_connect_meter(request, meter_name_or_id):
    tap = get_tap_from_meter_name_or_404(meter_name_or_id)
    form = forms.ConnectMeterForm(request.POST)
    if form.is_valid():
        tap = request.backend.connect_meter(tap, form.cleaned_data['meter'])
    else:
        raise kbapi.BadRequestError, _form_errors(form)
    return protolib.ToProto(tap, full=True)


@require_http_methods(["POST"])
@csrf_exempt
@auth_required
def tap_disconnect_meter(request, meter_name_or_id):
    tap = get_tap_from_meter_name_or_404(meter_name_or_id)
    tap = request.backend.connect_meter(tap, None)
    return protolib.ToProto(tap, full=True)


@require_http_methods(["POST"])
@csrf_exempt
@auth_required
def tap_connect_toggle(request, meter_name_or_id):
    tap = get_tap_from_meter_name_or_404(meter_name_or_id)
    form = forms.ConnectToggleForm(request.POST)
    if form.is_valid():
        tap = request.backend.connect_toggle(tap, form.cleaned_data['toggle'])
    else:
        raise kbapi.BadRequestError, _form_errors(form)
    return protolib.ToProto(tap, full=True)


@require_http_methods(["POST"])
@csrf_exempt
@auth_required
def tap_disconnect_toggle(request, meter_name_or_id):
    tap = get_tap_from_meter_name_or_404(meter_name_or_id)
    tap = request.backend.connect_toggle(tap, None)
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
        drink = request.backend.record_drink(tap,
            ticks=cd['ticks'],
            volume_ml=cd.get('volume_ml'),
            username=cd.get('username'),
            pour_time=pour_time,
            duration=duration,
            shout=cd.get('shout'),
            tick_time_series=cd.get('tick_time_series'),
            photo=request.FILES.get('photo', None))
        return protolib.ToProto(drink, full=True)
    except backend.exceptions.BackendError, e:
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
        res = request.backend.cancel_drink(drink_id=cd.get('id'), spilled=cd.get('spilled', False))
        return protolib.ToProto(res, full=True)
    except backend.exceptions.BackendError, e:
        raise kbapi.ServerError(str(e))


@require_http_methods(["POST"])
@csrf_exempt
def login(request):
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        auth_login(request, form.get_user())
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return RESULT_OK
    else:
        raise kbapi.PermissionDeniedError('Login failed.')


def logout(request):
    auth_logout(request)
    return RESULT_OK


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
        email = form.cleaned_data.get('email', None)
        password = form.cleaned_data.get('password', None)
        photo = request.FILES.get('photo', None)
        try:
            user = request.backend.create_new_user(username, email=email,
                password=password, photo=photo)
            return protolib.ToProto(user, full=True)
        except backend.exceptions.UserExistsError:
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
    mugshot = user.mugshot
    if not mugshot:
        return {}
    return mugshot


def post_user_photo(request, user):
    photo_file = request.FILES.get('photo')
    if not photo_file:
        raise kbapi.BadRequestError('The file "photo" is required.')

    pic = models.Picture.objects.create(user=user)
    pic.image.save(photo_file.name, photo_file)
    pic.save()

    user.mugshot = pic
    user.save()
    return protolib.ToProto(pic)


@csrf_exempt
@require_http_methods(["POST"])
def link_device_new(request):
    name = request.POST.get('name', 'Unknown Device')
    code = devicelink.start_link(name)
    return {'status': 'ok', 'code': code, 'linked': False}


@require_http_methods(["GET"])
def link_device_status(request, code):
    try:
        api_key = devicelink.get_status(code)
    except devicelink.LinkExpiredException:
        raise Http404('Code expired or does not exist.')
    if api_key:
        return {'status': 'ok', 'linked': True, 'api_key': api_key}
    return {'status': 'ok', 'linked': False}


def default_handler(request):
    raise Http404('Not an API endpoint: %s' % request.path[:100])


def get_tap_from_meter_name_or_404(meter_name_or_id):
    try:
        meter_id = int(meter_name_or_id)
        try:
            return models.KegTap.objects.get(pk=meter_id)
        except models.KegTap.DoesNotExist as e:
            raise Http404(str(e))
    except ValueError:
        pass

    try:
        return models.KegTap.get_from_meter_name(meter_name_or_id)
    except models.KegTap.DoesNotExist, e:
        raise Http404(str(e))
