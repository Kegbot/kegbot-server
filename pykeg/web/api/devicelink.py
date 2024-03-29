"""Protocol for associating new frontend devices with a Kegbot server.

The protocol consists of three phases, ultimately granting the requesting
device (client) a new API key to Kegbot Server.

Protocol:

    1. Client initiates a new pairing session by POSTing to
       `/api/devices/link`.

    2. Server generates a new opaque and unguessable short-lived
       pairing token (`start_link()`) and returns it to the client.

    3. Client displays the pairing token on its screen, and continuously
       polls its status via `/api/devices/status/<token>` (`get_status()`).

    4. User logs in to the web interface and confirms the request by
       entering the same access token into a form, causing the token
       to be marked as validated (`confirm_link()`).

    5. On next subsequent poll of `/api/devices/status/<token>`, the
       request handler discovers the token has been confirm, creates
       a new Device record and ApiKey, and returns the ApiKey.
"""

import random
from builtins import range

from django.core.cache import cache

from pykeg.core import models

CACHE_PREFIX = "devicelink:"
CACHE_TIMEOUT = 60 * 60

# Letters used to build a new device link code.  Currently
# A-Z,0-9 sans visually-ambiguous characters {I, 1, O, 0}.
CODE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

# Default code size generated by _build_code.  Entropy of the pairing
# code is:
#
#   len(CODE_LETTERS) ** DEFAULT_CODE_SIZE
#
# Entropy is only needed to prevent collisions of active pairing
# sessions, and not for security of the protocol (since an attacker
# still needs a logged-in admin session cookie to accept a
# guessed code).
DEFAULT_CODE_SIZE = 6


class LinkExpiredException(Exception):
    """Link code not found."""


def _build_code(size=DEFAULT_CODE_SIZE):
    code = "".join(random.choice(CODE_LETTERS) for i in range(size))
    mid = size // 2
    code = "{}-{}".format(code[:mid], code[mid:])
    return code


def _get_status(code):
    cache_key = "".join((CACHE_PREFIX, code))
    status = cache.get(cache_key)
    return status


def _set_status(code, status):
    cache_key = "".join((CACHE_PREFIX, code))
    cache.set(cache_key, status, timeout=CACHE_TIMEOUT)


def start_link(name):
    """Starts a new link, by allocating and returning a link code."""
    if not name:
        raise ValueError("Must specify a name.")
    code = _build_code()
    _set_status(code, {"name": name, "linked": False})
    return code


def confirm_link(code):
    """Confirms a link, ie, flips its status to True."""
    status = _get_status(code)
    if not status:
        raise LinkExpiredException("Code not found")
    status["linked"] = True
    _set_status(code, status)
    return status


def get_status(code):
    """Gets status, finishing the link if true.

    Returns: string api key on link, None otherwise
    """
    status = _get_status(code)
    if not status:
        raise LinkExpiredException("Code not found")
    if status.get("linked"):
        cache_key = "".join((CACHE_PREFIX, code))
        cache.delete(cache_key)
        device = models.Device.objects.create(name=status.get("name"))
        apikey = models.ApiKey.objects.create(description="Linked device.", device=device)
        return apikey.key
    return None
