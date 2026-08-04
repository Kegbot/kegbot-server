"""Transient kegboard state, kept in redis.

Only two things about a kegboard are durable: a paired controller's
bearer token (Controller.auth_token) and a drink's pour_id. Everything
else here is either self-refreshing (the device roster: boards
re-announce every few seconds while unpaired and every heartbeat once
paired) or short-lived by nature (the one-shot token delivery slot,
the dedup cursor, pending commands, live pour updates), so losing
redis costs at most a re-approval click — never a credential and
never a drink.
"""

import secrets
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

ROSTER_KEY = "kegboard:device:{name}"
TOKEN_SLOT_KEY = "kegboard:token-delivery:{name}"
CURSOR_KEY = "kegboard:cursor:{name}"
COMMANDS_KEY = "kegboard:commands:{name}"
POUR_UPDATE_KEY = "kegboard:pour-update:{tap_id}"

# Devices are dropped from the roster when silent this long. Matches
# the protocol's 7-day dedup retention guidance.
ROSTER_TTL = int(timedelta(days=7).total_seconds())
CURSOR_TTL = ROSTER_TTL
# The board polls every 5s while pairing; an hour is generous.
TOKEN_SLOT_TTL = int(timedelta(hours=1).total_seconds())
# Commands are re-sent until acked; authorize/deny are stale within
# minutes regardless (the drinker is standing at the tap).
COMMANDS_TTL = int(timedelta(hours=1).total_seconds())
POUR_UPDATE_TTL = 10

STATE_PENDING = "pending"
STATE_DENIED = "denied"
# Approved from the dashboard; token staged but not yet picked up.
STATE_ALLOWED = "allowed"
STATE_PAIRED = "paired"


def mint_token():
    return f"kbe_{secrets.token_hex(20)}"


def mint_command_id():
    return f"cmd_{secrets.token_hex(4)}"


# Device roster: pairing candidates and paired-device health.


def get_device(name):
    return cache.get(ROSTER_KEY.format(name=name))


def list_devices():
    # cache.keys() returns decorated raw keys (prefix/version); recover
    # the device name from the suffix and re-fetch through the cache api.
    marker = ROSTER_KEY.format(name="")
    names = [key.rsplit(marker, 1)[1] for key in cache.keys(ROSTER_KEY.format(name="*"))]
    entries = [get_device(name) for name in sorted(set(names))]
    return sorted(
        (entry for entry in entries if entry),
        key=lambda entry: entry.get("last_seen") or "",
        reverse=True,
    )


def update_device(name, **fields):
    """Merges fields into the device's roster entry, refreshing its TTL."""
    now = timezone.now().isoformat()
    entry = get_device(name) or {"device": name, "first_seen": now, "state": STATE_PENDING}
    entry["last_seen"] = now
    entry.update(fields)
    cache.set(ROSTER_KEY.format(name=name), entry, ROSTER_TTL)
    return entry


def set_device_state(name, state):
    return update_device(name, state=state)


def forget_device(name):
    cache.delete(ROSTER_KEY.format(name=name))
    cache.delete(CURSOR_KEY.format(name=name))
    cache.delete(COMMANDS_KEY.format(name=name))
    cache.delete(TOKEN_SLOT_KEY.format(name=name))


# One-shot token delivery.


def stage_token(name, token):
    """Arms the pairing slot: the device's next poll receives the token."""
    cache.set(TOKEN_SLOT_KEY.format(name=name), token, TOKEN_SLOT_TTL)


def take_staged_token(name):
    """Consumes the slot; the token is never deliverable twice."""
    key = TOKEN_SLOT_KEY.format(name=name)
    token = cache.get(key)
    if token is not None:
        cache.delete(key)
    return token


# Dedup cursor: (boot_id, last processed event id) per device. The
# device queue is RAM-only, so once a new boot_id appears, older-boot
# events can never arrive again — one cursor per device suffices.


def get_cursor(name):
    return cache.get(CURSOR_KEY.format(name=name))


def set_cursor(name, boot_id, last_id):
    cache.set(CURSOR_KEY.format(name=name), {"boot_id": boot_id, "last_id": last_id}, CURSOR_TTL)


# Server -> device command queue. Commands ride every 200 response
# until the device acknowledges them with a command_result event.


def queue_command(name, command_type, data):
    command = {"id": mint_command_id(), "type": command_type, "data": data}
    commands = cache.get(COMMANDS_KEY.format(name=name)) or []
    commands.append(command)
    cache.set(COMMANDS_KEY.format(name=name), commands, COMMANDS_TTL)
    return command


def pending_commands(name):
    return cache.get(COMMANDS_KEY.format(name=name)) or []


def ack_command(name, command_id):
    key = COMMANDS_KEY.format(name=name)
    commands = [c for c in (cache.get(key) or []) if c["id"] != command_id]
    cache.set(key, commands, COMMANDS_TTL)


# Live pour state, for the (future) realtime UI.


def stash_pour_update(tap_id, data):
    cache.set(POUR_UPDATE_KEY.format(tap_id=tap_id), data, POUR_UPDATE_TTL)


def get_pour_update(tap_id):
    return cache.get(POUR_UPDATE_KEY.format(tap_id=tap_id))
