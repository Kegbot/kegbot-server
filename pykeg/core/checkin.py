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

"""Checks a central server for updates."""

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from pykeg.core import models
from pykeg.core import util
from pykeg.core.tasks import core_checkin_task
from pykeg.core.util import SuppressTaskErrors

import datetime
import logging
import os
import requests

FIELD_REG_ID = 'reg_id'
FIELD_PRODUCT = 'product'
FIELD_VERSION = 'version'

FIELD_INTERVAL_MILLIS = 'interval_millis'
FIELD_UPDATE_AVAILABLE = 'update_available'
FIELD_UPDATE_REQUIRED = 'update_required'
FIELD_UPDATE_TITLE = 'update_title'
FIELD_UPDATE_URL = 'update_url'
FIELD_NEWS = 'news'

PRODUCT = 'kegbot-server'

CHECKIN_URL = os.getenv('CHECKIN_URL', None) or 'https://kegbotcheckin.appspot.com/checkin'
CHECKIN_INTERVAL = datetime.timedelta(hours=12)

KEY_LAST_CHECKIN_TIME = 'checkin:last_checkin_time'
KEY_LAST_CHECKIN_RESPONSE = 'checkin:last_checkin_response'

LOGGER = logging.getLogger('checkin')
logging.getLogger('requests').setLevel(logging.WARNING)


class CheckinError(Exception):
    """Base exception."""


def get_last_checkin():
    """Returns tuple of (time, data), or (None, None) if not available."""
    return cache.get(KEY_LAST_CHECKIN_TIME), cache.get(KEY_LAST_CHECKIN_RESPONSE)


def set_last_checkin(when, response_data=None):
    """Sets last checkin date and time."""
    cache.set(KEY_LAST_CHECKIN_TIME, when, timeout=None)
    cache.set(KEY_LAST_CHECKIN_RESPONSE, response_data, timeout=None)


def schedule_checkin(force=False):
    """Schedules a checkin if needed and allowed.

    Args
        force: if True, ignore last checkin time.

    Returns
        True if a checkin was scheduled.
    """
    if settings.EMBEDDED:
        LOGGER.debug('schedule_checkin: not scheduling: site is embedded')
        return False

    kbsite = models.KegbotSite.get()
    if not kbsite.check_for_updates:
        LOGGER.debug('schedule_checkin: not scheduling: checkin disabled')
        return False

    last_checkin_time, last_checkin_data = get_last_checkin()
    now = timezone.now()
    if not last_checkin_time or (now - last_checkin_time) > CHECKIN_INTERVAL or force:
        with SuppressTaskErrors(LOGGER):
            LOGGER.info('schedule_checkin: scheduling checkin')
            core_checkin_task.delay()
            return True

    return False


def checkin(url=CHECKIN_URL, product=PRODUCT, timeout=None, quiet=False):
    """Issue a single checkin to the checkin server.

    No-op if kbsite.check_for_updates is False.

    Returns
        A checkin response dictionary, or None if checkin is disabled.

    Raises
        ValueError: On malformed reponse.
        requests.RequestException: On error talking to server.
    """
    if settings.EMBEDDED:
        LOGGER.debug('Checkin disabled in embedded mode')
        return

    kbsite = models.KegbotSite.get()
    if not kbsite.check_for_updates:
        LOGGER.debug('Upgrade check is disabled')
        return

    site = models.KegbotSite.get()
    reg_id = site.registration_id

    headers = {
        'User-Agent': util.get_user_agent(),
    }
    payload = {
        FIELD_PRODUCT: product,
        FIELD_REG_ID: reg_id,
        FIELD_VERSION: util.get_version(),
    }

    try:
        LOGGER.debug('Checking in, url=%s reg_id=%s' % (url, reg_id))
        result = requests.post(url, data=payload, headers=headers, timeout=timeout).json()
        new_reg_id = result.get(FIELD_REG_ID)
        if new_reg_id != reg_id:
            LOGGER.debug('Updating reg_id=%s' % new_reg_id)
            site.registration_id = new_reg_id
            site.save()
        LOGGER.debug('Checkin result: %s' % str(result))
        if not quiet:
            LOGGER.info('Checkin complete, reg_id=%s' % (reg_id,))
        set_last_checkin(timezone.now(), result)
        return result
    except (ValueError, requests.RequestException) as e:
        if not quiet:
            LOGGER.warning('Checkin error: %s' % str(e))
        raise CheckinError(e)
