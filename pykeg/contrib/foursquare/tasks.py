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

"""Celery tasks for Foursquare."""

import foursquare
from celery.task import task
import datetime
from pykeg.plugin import util

MAX_CHECKIN_AGE = datetime.timedelta(minutes=30)

logger = util.get_logger(__name__)

@task(expires=60)
def checkin(token, venue_id):
    client = foursquare.Foursquare(access_token=token)
    logger.info('Checkin request: token=%s venue=%s' % (token, venue_id))

    last_checkin = _get_last_checkin(client)
    if last_checkin:
        venue = last_checkin.get('venue', {}).get('id', '')
        if venue == venue_id:
            when = datetime.datetime.fromtimestamp(int(last_checkin.get('createdAt', 0)))
            if (when + MAX_CHECKIN_AGE) > datetime.datetime.now():
                logger.info('Reusing last checkin.')
                return last_checkin
    logger.info('Performing fresh checkin.')
    return client.checkins.add(params={'venueId': venue_id}).get('checkin')


def _get_last_checkin(client):
    result = client.users.checkins(params={'limit': 1})
    items = result.get('checkins', {}).get('items', [])
    if items:
        return items[0]
    return None
