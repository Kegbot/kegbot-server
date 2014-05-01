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
from django.core.cache import cache
from pykeg.core import models

CACHE_PREFIX = 'devicelink:'
CACHE_TIMEOUT = 60 * 60
CODE_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


class LinkExpiredException(Exception):
    """Link code not found."""


def _build_code(size=6):
    code = ''.join(random.choice(CODE_LETTERS) for i in range(size))
    code = '{}-{}'.format(code[:(size / 2)], code[(size / 2):])
    return code


def _get_status(code):
    cache_key = ''.join((CACHE_PREFIX, code))
    status = cache.get(cache_key)
    return status


def _set_status(code, status):
    cache_key = ''.join((CACHE_PREFIX, code))
    cache.set(cache_key, status, timeout=CACHE_TIMEOUT)


def start_link(name):
    """Starts a new link, by allocating and returning a link code."""
    if not name:
        raise ValueError('Must specify a name.')
    code = _build_code()
    _set_status(code, {'name': name, 'linked': False})
    return code


def confirm_link(code):
    """Confirms a link, ie, flips its status to True."""
    status = _get_status(code)
    if not status:
        raise LinkExpiredException('Code not found')
    status['linked'] = True
    _set_status(code, status)
    return status


def get_status(code):
    """Gets status, finishing the link if true.

    Returns: string api key on link, None otherwise
    """
    status = _get_status(code)
    if not status:
        raise LinkExpiredException('Code not found')
    if status.get('linked'):
        cache_key = ''.join((CACHE_PREFIX, code))
        cache.delete(cache_key)
        device = models.Device.objects.create(name=status.get('name'))
        apikey = models.ApiKey.objects.create(description='Linked device.', device=device)
        return apikey.key
    return None
