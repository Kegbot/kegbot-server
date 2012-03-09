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

from django.db import models
from pykeg.core import models as core_models
from socialregistration import signals as sr_signals
from socialregistration.contrib.foursquare.models import FoursquareProfile

### Site-specific

class SiteFoursquareSettings(models.Model):
  site = models.OneToOneField(core_models.KegbotSite, unique=True,
      related_name='foursquare_settings')
  venue_id = models.CharField(max_length=256,
      help_text='The foursquare venue id for this Kegbot.')
  venue_name = models.CharField(max_length=256,
      help_text='The foursquare venue name for this Kegbot.')

### User-specific

class FoursquareSettings(models.Model):
  profile = models.OneToOneField(FoursquareProfile, unique=True,
      related_name='settings')
  enabled = models.BooleanField(default=True,
      help_text='Deselect to disable all foursquare activity.')
  checkin_session_joined = models.BooleanField(default=True,
      help_text='Checkin when I start drinking.')

def _foursquare_connect_handler(sender, user, profile, client, request=None, **kwargs):
  settings, _ = FoursquareSettings.objects.get_or_create(profile=profile)
  settings.save()

sr_signals.connect.connect(_foursquare_connect_handler, sender=FoursquareProfile,
    dispatch_uid = 'foursquare.connect')

