"""Serializes model objects for legacy API responses.

Replaces the old protobuf round-trip (``pykeg.proto.protolib``): each
converter builds a plain dict with the same field names and presence
rules the protobuf encoding produced. Fields the old encoding marked
deprecated are omitted.
"""

from addict import Dict

from pykeg.core import models

_CONVERSION_MAP = {}


def converts(kind):
    def decorate(f):
        _CONVERSION_MAP[kind] = f
        return f

    return decorate


def datestr(dt):
    return dt.isoformat()


def to_dict(obj, full=False):
    """Converts a model instance (or iterable of them) to a response dict."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return Dict(obj)
    if hasattr(obj, "__iter__"):
        return [to_dict(item, full) for item in obj]
    kind = obj.__class__
    if kind in _CONVERSION_MAP:
        return Dict(_CONVERSION_MAP[kind](obj, full))
    raise ValueError(f"Unknown object type: {kind}")


@converts(models.AuthenticationToken)
def auth_token_to_dict(record, full=False):
    ret = {
        "id": record.id,
        "auth_device": record.auth_device,
        "token_value": record.token_value,
        "created_time": datestr(record.created_time),
        "enabled": record.enabled,
    }
    if record.user_id:
        ret["username"] = str(record.user.username)
        ret["user"] = to_dict(record.user)
    if record.nice_name:
        ret["nice_name"] = record.nice_name
    if record.expire_time:
        ret["expire_time"] = datestr(record.expire_time)
    if record.pin:
        ret["pin"] = record.pin
    return ret


@converts(models.Picture)
def picture_to_dict(record, full=False, use_png=False):
    if use_png:
        ret = {
            "url": record.resized_png.url,
            "thumbnail_url": record.thumbnail_png.url,
        }
    else:
        ret = {
            "url": record.resized.url,
            "thumbnail_url": record.thumbnail.url,
        }
    ret["original_url"] = record.image.url
    if record.time:
        ret["time"] = datestr(record.time)
    if record.caption:
        ret["caption"] = record.caption
    if record.user_id:
        ret["user_id"] = record.user.username
    if record.keg_id:
        ret["keg_id"] = record.keg_id
    if record.session_id:
        ret["session_id"] = record.session_id
    return ret


@converts(models.Beverage)
def beverage_to_dict(beverage, full=False):
    ret = {
        "id": beverage.id,
        "name": beverage.name,
        "producer": to_dict(beverage.producer, full),
        "beverage_type": beverage.beverage_type,
    }
    if beverage.style:
        ret["style"] = beverage.style
    if beverage.description:
        ret["description"] = beverage.description
    if beverage.picture:
        # Use PNG for beverages.
        ret["picture"] = picture_to_dict(beverage.picture, full=full, use_png=True)
    if beverage.vintage_year:
        ret["vintage_year"] = beverage.vintage_year.year
    if beverage.abv_percent is not None:
        ret["abv_percent"] = beverage.abv_percent
    if beverage.calories_per_ml is not None:
        ret["calories_per_ml"] = beverage.calories_per_ml
    if beverage.carbs_per_ml is not None:
        ret["carbs_per_ml"] = beverage.carbs_per_ml
    if beverage.original_gravity is not None:
        ret["original_gravity"] = beverage.original_gravity
    if beverage.specific_gravity is not None:
        ret["specific_gravity"] = beverage.specific_gravity
    if beverage.untappd_beer_id is not None:
        ret["untappd_id"] = str(beverage.untappd_beer_id)
    if beverage.color_hex:
        ret["color_hex"] = beverage.color_hex
    if beverage.srm:
        ret["srm"] = beverage.srm
    if beverage.ibu:
        ret["ibu"] = beverage.ibu
    if beverage.star_rating is not None:
        ret["star_rating"] = beverage.star_rating
    if beverage.beverage_backend is not None:
        ret["beverage_backend"] = beverage.beverage_backend
    if beverage.beverage_backend_id is not None:
        ret["beverage_backend_id"] = beverage.beverage_backend_id
    return ret


@converts(models.BeverageProducer)
def producer_to_dict(producer, full=False):
    ret = {
        "id": producer.id,
        "name": producer.name,
        "is_homebrew": bool(producer.is_homebrew),
    }
    if producer.country is not None:
        ret["country"] = producer.country
    if producer.origin_state is not None:
        ret["origin_state"] = producer.origin_state
    if producer.origin_city is not None:
        ret["origin_city"] = producer.origin_city
    if producer.url is not None:
        ret["url"] = producer.url
    if producer.description is not None:
        ret["description"] = producer.description
    if producer.picture:
        ret["picture"] = to_dict(producer.picture)
    return ret


@converts(models.Controller)
def controller_to_dict(controller, full=False):
    ret = {
        "id": controller.id,
        "name": controller.name,
    }
    if controller.model_name:
        ret["model_name"] = controller.model_name
    if controller.serial_number:
        ret["serial_number"] = controller.serial_number
    return ret


@converts(models.FlowMeter)
def flow_meter_to_dict(flow_meter, full=False):
    return {
        "id": flow_meter.id,
        "name": flow_meter.meter_name(),
        "controller": to_dict(flow_meter.controller),
        "port_name": flow_meter.port_name,
        "ticks_per_ml": flow_meter.ticks_per_ml,
    }


@converts(models.FlowToggle)
def flow_toggle_to_dict(flow_toggle, full=False):
    return {
        "id": flow_toggle.id,
        "name": flow_toggle.toggle_name(),
        "controller": to_dict(flow_toggle.controller),
        "port_name": flow_toggle.port_name,
    }


@converts(models.Drink)
def drink_to_dict(drink, full=False):
    ret = {
        "id": drink.id,
        "url": str(drink.get_absolute_url()),
        "ticks": drink.ticks,
        "volume_ml": drink.volume_ml,
        "session_id": drink.session_id,
        "time": datestr(drink.time),
        "duration": drink.duration,
    }
    if drink.keg:
        ret["keg_id"] = drink.keg_id
    if drink.user_id:
        ret["user_id"] = drink.user.username
    if drink.shout:
        ret["shout"] = drink.shout
    if drink.tick_time_series:
        ret["tick_time_series"] = drink.tick_time_series

    if full:
        if drink.user_id:
            ret["user"] = to_dict(drink.user)
        if drink.keg:
            ret["keg"] = to_dict(drink.keg)
        if drink.session:
            ret["session"] = to_dict(drink.session)
        if drink.picture:
            ret["images"] = [to_dict(drink.picture)]
    return ret


@converts(models.Keg)
def keg_to_dict(keg, full=False):
    ret = {
        "id": keg.id,
        "keg_type": keg.keg_type,
        "remaining_volume_ml": float(keg.remaining_volume_ml()),
        "full_volume_ml": keg.full_volume_ml,
        "served_volume_ml": keg.served_volume_ml,
        "spilled_volume_ml": keg.spilled_ml,
        "percent_full": keg.percent_full(),
        "start_time": datestr(keg.start_time),
        "end_time": datestr(keg.end_time),
        "online": keg.is_on_tap(),
        "beverage": to_dict(keg.type),
        "illustration_url": keg.get_illustration(thumbnail=False),
        "illustration_thumbnail_url": keg.get_illustration(thumbnail=True),
    }
    if keg.description is not None:
        ret["description"] = keg.description
    return ret


@converts(models.KegTap)
def keg_tap_to_dict(tap, full=False):
    ret = {
        "id": tap.id,
        "name": tap.name,
        "sort_order": tap.sort_order,
    }
    meter = tap.current_meter()
    if meter:
        ret["meter_name"] = meter.meter_name()
        ret["ml_per_tick"] = 1 / meter.ticks_per_ml
        ret["meter"] = to_dict(meter)
    else:
        ret["meter_name"] = f"unknown.{tap.id}"
        ret["ml_per_tick"] = 0

    toggle = tap.current_toggle()
    if toggle:
        ret["relay_name"] = toggle.toggle_name()
        ret["toggle"] = to_dict(toggle)
    else:
        ret["relay_name"] = ""

    if tap.current_keg:
        ret["current_keg_id"] = tap.current_keg_id
        if full:
            ret["current_keg"] = to_dict(tap.current_keg, full=True)

    if tap.temperature_sensor:
        ret["thermo_sensor"] = to_dict(tap.temperature_sensor)
        ret["thermo_sensor_id"] = tap.temperature_sensor_id
        log = tap.temperature_sensor.LastLog()
        if log:
            ret["last_temperature"] = to_dict(log)
    return ret


@converts(models.DrinkingSession)
def session_to_dict(record, full=False):
    ret = {
        "id": record.id,
        "url": str(record.get_absolute_url()),
        "start_time": datestr(record.start_time),
        "end_time": datestr(record.end_time),
        "volume_ml": record.volume_ml,
        "name": record.name or "",
    }
    if full:
        ret["is_active"] = record.IsActiveNow()
    return ret


@converts(models.Thermolog)
def thermo_log_to_dict(record, full=False):
    return {
        "id": record.id,
        "sensor_id": record.sensor_id,
        "temperature_c": record.temp,
        "time": datestr(record.time),
    }


@converts(models.ThermoSensor)
def thermo_sensor_to_dict(record, full=False):
    ret = {
        "id": record.id,
        "sensor_name": record.raw_name,
        "nice_name": record.nice_name,
    }
    log = record.LastLog()
    if log:
        ret["last_log"] = to_dict(log)
    return ret


@converts(models.User)
def user_to_dict(user, full=False):
    ret = {
        "username": user.username,
        "url": str(user.get_absolute_url()),
        "is_active": user.is_active,
        "display_name": user.get_full_name(),
    }
    if full:
        ret["email"] = user.email
        ret["is_staff"] = user.is_staff
        ret["is_superuser"] = user.is_superuser
        ret["last_login"] = datestr(user.last_login or user.date_joined)
        ret["date_joined"] = datestr(user.date_joined)
    if user.mugshot_id:
        ret["image"] = to_dict(user.mugshot)
    return ret


@converts(models.SystemEvent)
def system_event_to_dict(record, full=False):
    ret = {
        "id": record.id,
        "kind": record.kind,
        "time": datestr(record.time),
    }
    if record.drink_id:
        ret["drink_id"] = record.drink_id
        if full:
            ret["drink"] = to_dict(record.drink, full=True)
    if record.keg_id:
        ret["keg_id"] = record.keg_id
        if full:
            ret["keg"] = to_dict(record.keg, full=True)
    if record.session_id:
        ret["session_id"] = record.session_id
        if full:
            ret["session"] = to_dict(record.session, full=True)
    if record.user_id:
        ret["user_id"] = str(record.user.username)
        if full:
            ret["user"] = to_dict(record.user, full=True)

    image = None
    if record.kind in ("drink_poured", "session_started", "session_joined") and record.user:
        image = record.user.mugshot
    elif record.kind in ("keg_tapped", "keg_ended"):
        if record.keg.type and record.keg.type.picture:
            image = record.keg.type.picture
    if image:
        ret["image"] = to_dict(image)
    return ret


def sync_dict(
    active_kegs=[],
    active_session=None,
    active_users=[],
    controllers=[],
    drinks=[],
    events=[],
    meters=[],
    site_title="",
    server_version="",
    taps=[],
    toggles=[],
):
    """Builds the composite status ("sync") response."""
    ret = Dict(
        {
            "site_info": {
                "title": site_title,
                "server_version": server_version,
            },
            "active_kegs": [to_dict(o) for o in active_kegs],
            "active_users": [to_dict(o) for o in active_users],
            "controllers": [to_dict(o) for o in controllers],
            "drinks": [to_dict(o) for o in drinks],
            "events": [to_dict(o) for o in events],
            "meters": [to_dict(o) for o in meters],
            "taps": [to_dict(o) for o in taps],
            "toggles": [to_dict(o) for o in toggles],
        }
    )
    if active_session:
        ret["active_session"] = to_dict(active_session)
    return ret
