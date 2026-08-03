"""Legacy (v1) API views.

This API is deprecated: only the endpoints kegbot-pycore uses (plus the
events feed used by the fullscreen page) are still served. Everything
else responds 410 Gone; new integrations should use the v2 API.
"""

import datetime
import logging
from functools import wraps

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from pykeg.core import models
from pykeg.core import util as core_util
from pykeg.web.api import exceptions, forms, serialize, util
from pykeg.web.api.forms import ControllerForm, NewFlowMeterForm

_LOGGER = logging.getLogger(__name__)

RESULT_OK = {"result": "ok"}

# Decorators


def auth_required(view_func):
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    util.set_needs_auth(wrapped_view)
    return wraps(view_func)(wrapped_view)


# Helpers


def _form_errors(form):
    ret = {}
    for field in form:
        if field.errors:
            name = field.html_name
            ret[name] = []
            for error in field.errors:
                ret[name].append(error)
    return ret


def _current_session():
    try:
        latest = models.DrinkingSession.objects.latest()
        if latest.IsActiveNow():
            return latest
    except models.DrinkingSession.DoesNotExist:
        pass
    return None


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
    except models.KegTap.DoesNotExist as e:
        raise Http404(str(e))


# Endpoints


@auth_required
def get_status(request):
    session = _current_session()

    controllers = models.Controller.objects.all()
    drinks = models.Drink.objects.all()[:5]
    events = models.SystemEvent.objects.all()[:5]
    kegs = models.Keg.objects.all().filter(status=models.Keg.STATUS_ON_TAP)
    meters = models.FlowMeter.objects.all()
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

    return serialize.sync_dict(
        active_kegs=kegs,
        active_session=session,
        active_users=current_users,
        controllers=controllers,
        drinks=drinks,
        events=events,
        meters=meters,
        site_title=title,
        server_version=version,
        taps=taps,
        toggles=toggles,
    )


@csrf_exempt
@auth_required
def all_controllers(request):
    if request.method == "POST":
        form = ControllerForm(request.POST)
        if form.is_valid():
            return form.save()
        else:
            errors = _form_errors(form)
            raise exceptions.BadRequestError(errors)

    return models.Controller.objects.all()


@csrf_exempt
@auth_required
def all_flow_meters(request):
    if request.method == "POST":
        form = NewFlowMeterForm(request.POST)
        if form.is_valid():
            return form.save()
        else:
            errors = _form_errors(form)
            raise exceptions.BadRequestError(errors)

    return models.FlowMeter.objects.all()


def all_events(request):
    events = models.SystemEvent.objects.all().order_by("-id")
    events = apply_since(request, events)
    events = events[:10]
    return [serialize.to_dict(e, full=True) for e in events]


def apply_since(request, query):
    """Restricts the query to `since` events, if given."""
    since_str = request.GET.get("since")
    if since_str:
        try:
            since = int(since_str)
            return query.filter(id__gt=since)
        except ValueError, TypeError:
            pass
    return query


@require_http_methods(["GET", "POST"])
@csrf_exempt
def all_taps(request):
    if request.method == "POST":
        util.check_api_key(request)
        return create_tap(request)
    return models.KegTap.objects.all().order_by("name")


def create_tap(request):
    form = forms.TapCreateForm(request.POST)
    if form.is_valid():
        return models.KegTap.create_tap(name=form.cleaned_data["name"])
    raise exceptions.BadRequestError(_form_errors(form))


@auth_required
def get_auth_token(request, auth_device, token_value):
    tok = get_object_or_404(
        models.AuthenticationToken, auth_device=auth_device, token_value=token_value
    )
    return tok


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
    if request.method == "POST":
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
        "sensor": serialize.to_dict(sensor),
        "last_temp": last_temp,
        "last_time": last_time,
    }
    return res


@auth_required
def _thermo_sensor_post(request, sensor_name):
    form = forms.ThermoPostForm(request.POST)
    if not form.is_valid():
        raise exceptions.BadRequestError(_form_errors(form))
    cd = form.cleaned_data
    sensor, _ = models.ThermoSensor.objects.get_or_create(raw_name=sensor_name)
    # TODO(mikey): use form fields to compute `when`
    return sensor.log_sensor_reading(cd["temp_c"])


@csrf_exempt
def tap_detail(request, meter_name_or_id):
    tap = get_tap_from_meter_name_or_404(meter_name_or_id)
    if request.method == "POST":
        util.check_api_key(request)
        return _tap_detail_post(request, tap)
    elif request.method == "GET":
        return serialize.to_dict(tap, full=True)

    raise exceptions.BadRequestError("Method not supported")


@auth_required
def _tap_detail_post(request, tap):
    form = forms.DrinkPostForm(request.POST)
    if not form.is_valid():
        raise exceptions.BadRequestError(_form_errors(form))
    cd = form.cleaned_data
    if cd.get("record_date"):
        pour_time = datetime.datetime.fromisoformat(cd.get("record_date"))
    elif cd.get("pour_time") and cd.get("now"):
        pour_time = datetime.datetime.fromtimestamp(cd.get("pour_time"))
        pour_now = datetime.datetime.fromtimestamp(cd.get("now"))
        pour_time_ago = pour_now - pour_time
        pour_time = timezone.now() - pour_time_ago
    else:
        pour_time = None
    duration = cd.get("duration")
    if duration is None:
        duration = 0

    drink = models.Drink.record_drink(
        tap,
        ticks=cd["ticks"],
        volume_ml=cd.get("volume_ml"),
        username=cd.get("username"),
        pour_time=pour_time,
        duration=duration,
        shout=cd.get("shout"),
        tick_time_series=cd.get("tick_time_series"),
        photo=request.FILES.get("photo", None),
    )
    return serialize.to_dict(drink, full=True)


@csrf_exempt
@auth_required
def cancel_drink(request):
    if request.method != "POST":
        raise exceptions.BadRequestError("POST required")
    form = forms.CancelDrinkForm(request.POST)
    if not form.is_valid():
        raise exceptions.BadRequestError(_form_errors(form))
    cd = form.cleaned_data
    drink = get_object_or_404(models.Drink, id=cd["id"])
    # Serialize before canceling: cancel_drink deletes the record.
    result = serialize.to_dict(drink, full=True)
    drink.cancel_drink(spilled=cd.get("spilled", False))
    return result


def gone(request):
    raise exceptions.GoneError(
        "This endpoint has been retired; the legacy API only serves "
        "kegbot-pycore. Use the v2 API instead."
    )
