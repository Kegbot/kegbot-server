# Copyright 2012 Mike Wakerly <opensource@hoho.com>
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

import datetime

from pykeg.connections import common
from pykeg.core import models as core_models
from socialregistration.contrib.foursquare import models as sr_foursquare_models
from . import models

import foursquare

from celery.task import task

logger = common.get_logger(__name__)

MAX_CHECKIN_AGE = datetime.timedelta(minutes=30)

@task
def checkin_event(event):
  if event.kind != 'session_joined' or not event.user:
    logger.info('Event not useful for foursquare checkin: %s' % event.kind)
    return False
  elif common.is_stale(event.time):
    logger.info('Event is stale, ignoring: %s' % str(event))
    return False

  site = event.site
  user = event.user

  client = _build_client(site, user)
  if not client:
    logger.info('foursquare client not available for site/user.')
    return

  result = get_or_create_fresh_checkin(site, user, client)
  logger.debug('Result: %s' % str(result))
  return True

def _build_client(site, user):
  try:
    site_settings = models.SiteFoursquareSettings.objects.get(site=site)
  except models.SiteFoursquareSettings.DoesNotExist:
    return None

  user = user
  try:
    user_profile = sr_foursquare_models.FoursquareProfile.objects.get(user=user)
  except sr_foursquare_models.FoursquareProfile.DoesNotExist:
    return None

  s = user_profile.settings
  if not s.enabled or not s.checkin_session_joined:
    return None

  client = foursquare.Foursquare(access_token=user_profile.access_token.access_token)
  return client

@task
def handle_new_picture(picture_id):
  picture = core_models.PourPicture.objects.get(id=picture_id)
  site = picture.site
  user = picture.user
  if not site or not user:
    logger.info('Picture does not have a site/user, ignoring.')
    return
  elif common.is_stale(picture.time):
    logger.info('Picture is stale, ignoring.')
    return

  client = _build_client(site, user)
  if not client:
    logger.info('foursquare client not available for site/user.')
    return

  checkin = get_or_create_fresh_checkin(site, user, client)
  if not checkin:
    logger.info('Cannot find a checkin for this user, ignoring picture.')
    return

  logger.info('Uploading photo to foursquare.')
  result = client.photos.add(photo_data=picture.picture.image.read(),
      params={'checkinId': checkin.get('id','') })
  logger.info('Upload complete, result: %s' % str(result))

def get_or_create_fresh_checkin(site, user, client):
  site_settings = models.SiteFoursquareSettings.objects.get(site=site)
  last_checkin = _get_last_checkin(client)
  if last_checkin:
    venue = last_checkin.get('venue', {}).get('id', '')
    if venue == site_settings.venue_id:
      when = datetime.datetime.fromtimestamp(int(last_checkin.get('createdAt', 0)))
      if (when + MAX_CHECKIN_AGE) > datetime.datetime.now():
        return last_checkin

  return client.checkins.add(params={'venueId': site_settings.venue_id}).get('checkin')

def _get_last_checkin(client):
  result = client.users.checkins(params={'limit': 1})
  items = result.get('checkins', {}).get('items', [])
  if items:
    return items[0]
  return None
