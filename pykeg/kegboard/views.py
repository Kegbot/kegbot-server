"""The kegboard event protocol endpoint (POST /kegboard-event).

Implements v1 of the protocol: bearer-token authentication with a
dashboard-driven pairing flow, at-least-once delivery made idempotent
by a per-boot cursor, and event processing that flows through the
existing domain models (record_drink, log_sensor_reading), so system
events and stats behave exactly as for any other drink.
"""

import logging
from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from pykeg.core import models

from . import state

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = 1
MAX_BODY_BYTES = 16 * 1024
# Idle limit for a token-created grant: flow resets it, so a slow glass
# stays alive; total lifetime is bounded by the device's own clamp.
AUTHORIZE_IDLE_MS = 30 * 1000


class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    type = serializers.CharField()
    age_ms = serializers.IntegerField(min_value=0)
    time = serializers.DateTimeField(required=False)
    data = serializers.DictField()


class EnvelopeSerializer(serializers.Serializer):
    v = serializers.IntegerField()
    device = serializers.CharField(max_length=64)
    boot_id = serializers.CharField(max_length=32)
    sent_uptime_ms = serializers.IntegerField(min_value=0)
    events = EventSerializer(many=True, min_length=1, max_length=16)


class PourSerializer(serializers.Serializer):
    meter_number = serializers.IntegerField(min_value=0)
    pour_id = serializers.CharField(max_length=64)
    volume_ml = serializers.FloatField(min_value=0)
    duration_ms = serializers.IntegerField(min_value=0)
    auth_device = serializers.CharField(required=False)
    auth_token = serializers.CharField(required=False)
    grant_id = serializers.CharField(max_length=64, required=False)
    ticks = serializers.IntegerField(min_value=0, required=False)
    ml_per_tick = serializers.FloatField(required=False)
    tick_series = serializers.CharField(required=False)


class PourUpdateSerializer(serializers.Serializer):
    meter_number = serializers.IntegerField(min_value=0)
    pour_id = serializers.CharField(max_length=64)
    volume_ml = serializers.FloatField(min_value=0)
    duration_ms = serializers.IntegerField(min_value=0)


class TemperatureSerializer(serializers.Serializer):
    sensor = serializers.CharField()
    temp_c = serializers.FloatField()


class TokenSerializer(serializers.Serializer):
    auth_device = serializers.CharField()
    token = serializers.CharField()
    action = serializers.ChoiceField(choices=["attached", "detached"])


class GrantEndSerializer(serializers.Serializer):
    meter_numbers = serializers.ListField(child=serializers.IntegerField(min_value=0))
    reason = serializers.ChoiceField(
        choices=["max_volume", "max_duration", "max_idle", "detach", "command", "replaced"]
    )
    grant_id = serializers.CharField(max_length=64)
    volume_ml = serializers.FloatField(min_value=0)
    duration_ms = serializers.IntegerField(min_value=0)
    auth_device = serializers.CharField(required=False)
    auth_token = serializers.CharField(required=False)


class StatusSerializer(serializers.Serializer):
    state = serializers.ChoiceField(choices=["boot", "heartbeat"])
    fw_version = serializers.CharField()
    uptime_ms = serializers.IntegerField(min_value=0)
    wifi_rssi_dbm = serializers.IntegerField(required=False)
    events_dropped = serializers.IntegerField(min_value=0)
    config = serializers.DictField()
    meters = serializers.ListField(child=serializers.DictField(), required=False)


class CommandResultSerializer(serializers.Serializer):
    command = serializers.CharField()
    result = serializers.ChoiceField(choices=["ok", "error", "unsupported"])
    message = serializers.CharField(required=False)


DATA_SERIALIZERS = {
    "pour": PourSerializer,
    "pour_update": PourUpdateSerializer,
    "temperature": TemperatureSerializer,
    "token": TokenSerializer,
    "status": StatusSerializer,
    "command_result": CommandResultSerializer,
    "grant_end": GrantEndSerializer,
}


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _bearer_token(request):
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if header.startswith("Bearer "):
        return header[len("Bearer ") :].strip() or None
    return None


def _pairing_response(device_name, request):
    """The 401 pairing flow for any request we can't authenticate."""
    staged = state.take_staged_token(device_name)
    if staged is not None:
        state.update_device(device_name, state=state.STATE_PAIRED, last_error=None)
        return JsonResponse({"pairing": {"state": "allowed", "token": staged}}, status=401)

    entry = state.get_device(device_name)
    if entry and entry.get("state") == state.STATE_DENIED:
        state.update_device(device_name, ip=_client_ip(request), last_error=None)
        return JsonResponse({"pairing": {"state": "denied"}}, status=401)

    state.update_device(
        device_name, state=state.STATE_PENDING, ip=_client_ip(request), last_error=None
    )
    return JsonResponse({"pairing": {"state": "pending"}}, status=401)


def _note_rejected_batch(request, error):
    """Pins a rejected batch to its device's roster entry, best effort.

    A board whose batches all 400 would otherwise be invisible on the
    dashboard while plainly "reporting" in the server logs.
    """
    data = request.data
    device_name = data.get("device") if isinstance(data, dict) else None
    if not isinstance(device_name, str) or not device_name or len(device_name) > 64:
        logger.warning(f"kegboard: rejected batch from unidentifiable device: {error}")
        return
    logger.warning(f"kegboard {device_name}: rejected batch: {error}")
    state.update_device(device_name, ip=_client_ip(request), last_error=str(error)[:300])


def _port_number(port_name, prefix):
    if port_name.startswith(prefix):
        try:
            return int(port_name[len(prefix) :])
        except ValueError:
            pass
    return None


def _find_meter(controller, number):
    return models.FlowMeter.objects.filter(controller=controller, port_name=f"flow{number}").first()


def _handle_pour(controller, data, event_time):
    meter = _find_meter(controller, data["meter_number"])
    if not meter or not meter.tap:
        logger.warning(
            f"kegboard {controller.name}: pour on unbound meter {data['meter_number']}, dropped"
        )
        return
    if models.Drink.objects.filter(pour_id=data["pour_id"]).exists():
        return
    # Identity never travels down: the pour echoes our grant_id and we
    # resolve the user from the grant record. No grant -> guest pour.
    username = None
    grant_id = data.get("grant_id")
    if grant_id:
        grant = state.get_grant(grant_id)
        if grant:
            username = grant.get("user")
        else:
            logger.warning(
                f"kegboard {controller.name}: unknown grant {grant_id!r}, recording as guest"
            )
    if username and not models.User.objects.filter(username=username).exists():
        logger.warning(f"kegboard {controller.name}: unknown user {username!r}, recording as guest")
        username = None
    try:
        models.Drink.record_drink(
            meter.tap,
            ticks=data.get("ticks") or 0,
            volume_ml=data["volume_ml"],
            username=username,
            pour_time=event_time,
            duration=data["duration_ms"] // 1000,
            tick_time_series=data.get("tick_series", ""),
            pour_id=data["pour_id"],
        )
    except ValueError as e:
        logger.warning(f"kegboard {controller.name}: pour dropped: {e}")


def _handle_pour_update(controller, data, event_time):
    meter = _find_meter(controller, data["meter_number"])
    if not meter or not meter.tap:
        return
    state.stash_pour_update(
        meter.tap_id,
        {
            "pour_id": data["pour_id"],
            "volume_ml": data["volume_ml"],
            "duration_ms": data["duration_ms"],
            "updated": timezone.now().isoformat(),
        },
    )


def _handle_temperature(controller, data, event_time):
    raw_name = f"{controller.name}.{data['sensor']}"
    sensor, _ = models.ThermoSensor.objects.get_or_create(
        raw_name=raw_name, defaults={"nice_name": data["sensor"]}
    )
    try:
        sensor.log_sensor_reading(data["temp_c"], when=event_time)
    except ValueError as e:
        logger.warning(f"kegboard {controller.name}: temperature dropped: {e}")


def _handle_token(controller, data, event_time):
    if data["action"] != "attached":
        # Detaches are audit-only; the grant lifecycle arrives via
        # grant_end events.
        logger.info(f"kegboard {controller.name}: token event: {data}")
        return

    token = models.AuthenticationToken.objects.filter(
        auth_device=data["auth_device"], token_value=data["token"]
    ).first()
    if token and token.IsActive() and token.user:
        # v1 policy: the grant covers every meter on the board. The
        # meter<->relay association is ours: energize the relays bound
        # to the granted meters' taps.
        meters = []
        tap_ids = set()
        for meter in controller.meters.all():
            number = _port_number(meter.port_name, "flow")
            if number is None:
                continue
            meters.append(number)
            if meter.tap_id is not None:
                tap_ids.add(meter.tap_id)
        relays = sorted(
            number
            for number in (
                _port_number(toggle.port_name, "relay")
                for toggle in controller.toggles.all()
                if toggle.tap_id in tap_ids
            )
            if number is not None
        )
        grant_id = state.mint_grant_id()
        state.store_grant(grant_id, token.user.username)
        state.queue_command(
            controller.name,
            "authorize",
            {
                "grant_id": grant_id,
                "meter_numbers": sorted(meters),
                "relay_numbers": relays,
                "max_idle_ms": AUTHORIZE_IDLE_MS,
                "auth_device": data["auth_device"],
                "token": data["token"],
            },
        )
    else:
        if token is None:
            reason = "Unknown token"
        elif not token.IsActive():
            reason = "Token is disabled"
        else:
            reason = "Token not assigned to a user"
        state.queue_command(
            controller.name,
            "deny",
            {"auth_device": data["auth_device"], "token": data["token"], "reason": reason},
        )


def _handle_status(controller, data, event_time):
    state.update_device(
        controller.name,
        state=state.STATE_PAIRED,
        fw_version=data["fw_version"],
        uptime_ms=data["uptime_ms"],
        wifi_rssi_dbm=data.get("wifi_rssi_dbm"),
        events_dropped=data["events_dropped"],
        config=data["config"],
        meters=data.get("meters"),
    )
    for entry in data.get("meters") or []:
        number = entry.get("meter_number")
        ml_per_tick = entry.get("ml_per_tick")
        if not isinstance(number, int) or not ml_per_tick:
            continue
        meter, _ = models.FlowMeter.objects.get_or_create(
            controller=controller, port_name=f"flow{number}"
        )
        ticks_per_ml = 1.0 / ml_per_tick
        if abs(meter.ticks_per_ml - ticks_per_ml) > 1e-9:
            meter.ticks_per_ml = ticks_per_ml
            meter.save(update_fields=["ticks_per_ml"])


def _handle_grant_end(controller, data, event_time):
    """Grant lifecycle bookkeeping.

    The pour events are the volume record; the grant totals here are
    snapshots for cross-checking. The grant record itself is kept until
    its TTL so queued pours delivered late still attribute.
    """
    logger.info(
        f"kegboard {controller.name}: grant {data['grant_id']} ended "
        f"({data['reason']}): {data['volume_ml']} mL over {data['duration_ms']} ms "
        f"on meters {data['meter_numbers']}"
    )


def _handle_command_result(controller, data, event_time):
    if data["result"] != "ok":
        logger.warning(f"kegboard {controller.name}: command {data['command']}: {data}")
    state.ack_command(controller.name, data["command"])


EVENT_HANDLERS = {
    "pour": _handle_pour,
    "pour_update": _handle_pour_update,
    "temperature": _handle_temperature,
    "token": _handle_token,
    "status": _handle_status,
    "command_result": _handle_command_result,
    "grant_end": _handle_grant_end,
}


@extend_schema(exclude=True)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def kegboard_event(request):
    """Receives a kegboard event batch; excluded from the api schema."""
    if getattr(request, "need_setup", False) or getattr(request, "need_upgrade", False):
        # 5xx keeps events queued on the device until the site is ready.
        return JsonResponse({"error": "setup_required"}, status=503)

    if len(request.body) > MAX_BODY_BYTES:
        return JsonResponse({"error": "too_large"}, status=413)

    envelope = EnvelopeSerializer(data=request.data)
    if not envelope.is_valid():
        _note_rejected_batch(request, f"invalid batch: {envelope.errors}")
        return JsonResponse({"error": "invalid", "detail": envelope.errors}, status=400)
    batch = envelope.validated_data
    if batch["v"] != PROTOCOL_VERSION:
        _note_rejected_batch(request, f"unsupported protocol version {batch['v']}")
        return JsonResponse({"error": "unsupported_version"}, status=400)

    device_name = batch["device"]
    token = _bearer_token(request)
    controller = (
        models.Controller.objects.filter(auth_token=token).first() if token is not None else None
    )
    if controller is None:
        return _pairing_response(device_name, request)

    state.update_device(
        controller.name, state=state.STATE_PAIRED, ip=_client_ip(request), last_error=None
    )

    # Dedup: ids are monotonic per boot and the device queue does not
    # survive reboot, so one (boot_id, last_id) cursor is complete.
    cursor = state.get_cursor(controller.name)
    last_seen_id = cursor["last_id"] if cursor and cursor["boot_id"] == batch["boot_id"] else 0

    received = timezone.now()
    max_id = last_seen_id
    for event in batch["events"]:
        if event["id"] <= last_seen_id:
            continue
        max_id = max(max_id, event["id"])
        handler = EVENT_HANDLERS.get(event["type"])
        if not handler:
            logger.debug(f"kegboard {controller.name}: ignoring event type {event['type']!r}")
            continue
        data_serializer = DATA_SERIALIZERS[event["type"]](data=event["data"])
        if not data_serializer.is_valid():
            logger.warning(
                f"kegboard {controller.name}: bad {event['type']} payload, dropped: "
                f"{data_serializer.errors}"
            )
            continue
        event_time = received - timedelta(milliseconds=event["age_ms"])
        handler(controller, data_serializer.validated_data, event_time)

    state.set_cursor(controller.name, batch["boot_id"], max_id)

    return Response({"commands": state.pending_commands(controller.name)})
