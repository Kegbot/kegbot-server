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

from pykeg.core import kbjson
from pykeg.core import util
from socialregistration.contrib.foursquare import models as sr_foursquare_models
from . import models

import foursquare

from celery.decorators import task

@task
def checkin_event(event):
  if event.kind != 'session_joined' or not event.user:
    print 'Event not tweetable: %s' % event
    return False
  do_checkin(event)
  return True

def do_checkin(event):
  site = event.site

  try:
    site_settings = models.SiteFoursquareSettings.objects.get(site=site)
  except models.SiteFoursquareSettings.DoesNotExist:
    print 'No foursquare settings for site'
    return

  user = event.user
  try:
    user_profile = sr_foursquare_models.FoursquareProfile.objects.get(user=user)
  except sr_foursquare_models.FoursquareProfile.DoesNotExist:
    print 'No foursquare profile for user: %s' % user
    return

  s = user_profile.settings
  if not s.enabled or not s.checkin_session_joined:
    print 'User has disabled foursquare.'
    return

  client = foursquare.Foursquare(access_token=user_profile.access_token.access_token)
  print client.checkins.add(params={'venueId': site_settings.venue_id})
