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

"""Celery tasks for Webhook plugin."""

from pykeg.celery import app
from pykeg.plugin import util
from pykeg.core.util import get_version
from kegbot.util import kbjson

import requests

logger = util.get_logger(__name__)


@app.task(name='webhook_post', expires=180)
def webhook_post(url, event_dict):
    """Posts an event to the supplied URL.

    The request body is a JSON dictionary of:
      * type: webhook message type (currently always 'event')
      * event_dict: webhook data (the event payload)

    Event payloads are in the same format as the /api/events/ endpoint.
    """
    logger.info('Posting webhook: url=%s event=%s' % (url, event_dict))

    hook_dict = {
        'type': 'event',
        'data': event_dict,
    }

    headers = {
        'content-type': 'application/json',
        'user-agent': 'Kegbot/%s' % get_version(),
    }

    try:
        return requests.post(url, data=kbjson.dumps(hook_dict), headers=headers)
    except requests.exceptions.RequestException, e:
        logger.warning('Error posting hook: %s' % e)
        return False
