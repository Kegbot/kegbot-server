"""Dashboard-side pairing operations for kegboard devices."""

from pykeg.core import models

from . import state


def list_devices():
    """Roster entries merged with paired controllers redis has forgotten.

    A paired board that hasn't spoken since redis last restarted has no
    roster entry but still holds a valid token; surface it (with no
    liveness data) so it can be revoked.
    """
    entries = {entry["device"]: dict(entry) for entry in state.list_devices()}
    paired_names = set(
        models.Controller.objects.filter(auth_token__isnull=False).values_list("name", flat=True)
    )
    for name, entry in entries.items():
        stale = entry.get("state") in (state.STATE_PAIRED, state.STATE_ALLOWED)
        if stale and name not in paired_names:
            # Token was revoked but the board hasn't re-announced yet.
            entry["state"] = state.STATE_PENDING
    for name in sorted(paired_names - set(entries)):
        entries[name] = {"device": name, "state": state.STATE_PAIRED}
    return list(entries.values())


def allow_device(name):
    """Approves a device: mints its token and arms the delivery slot.

    The controller row is created (or reused) immediately so taps can
    be configured before the board even picks up its token. Re-allowing
    a revoked or token-lost device replaces the old token.
    """
    token = state.mint_token()
    controller, created = models.Controller.objects.get_or_create(
        name=name, defaults={"model_name": "Kegboard"}
    )
    controller.auth_token = token
    controller.save(update_fields=["auth_token"])
    state.stage_token(name, token)
    state.set_device_state(name, state.STATE_ALLOWED)
    return controller


def deny_device(name):
    state.set_device_state(name, state.STATE_DENIED)


def revoke_device(name):
    """Revokes the device's token; its next request re-enters pairing.

    The controller row (and its meters, taps, drink history) is kept.
    """
    models.Controller.objects.filter(name=name).update(auth_token=None)
    state.forget_device(name)


def forget_device(name):
    """Drops a pending/denied device from the roster."""
    state.forget_device(name)
