# Copyright 2013 Mike Wakerly <opensource@hoho.com>
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

"""Celery tasks for Untappd."""

import requests
import urllib
import datetime
from pykeg.plugin import util
from celery.task import task

logger = util.get_logger(__name__)

@task(expires=60)
def checkin(token, beer_id, timezone_name, shout=None):
    logger.info('Checking in: token=%s beer_id=%s timezone_name=%s' % (token, beer_id, timezone_name))

    # TODO(mikey): API does not appear to support Olso tz names for
    # the timezone parameter.  Report as GMT, as it doesn't seem to
    # be meaningful.
    data = {
        'bid': beer_id,
        'gmt_offset': 0,
        'timezone': 'GMT',
    }

    if shout:
        data['shout'] = shout

    params = {'access_token': token}
    url = 'https://api.untappd.com/v4/checkin/add'
    r = requests.post(url, params=params, data=data)
    logger.info('Response: %s' % str(r.text))
