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

### Helpers

class _SettingsMixin(models.Model):
  """Common settings for all social accounts."""
  class Meta:
    abstract = True

  enabled = models.BooleanField(default=True,
      help_text='Deselect to disable all posting from this account.')
  post_session_joined = models.BooleanField(default=True,
      help_text='Tweet at the start of a new drinking session.')
  post_drink_poured = models.BooleanField(default=False,
      help_text='Tweet when a new drink is poured.')

### Site-specific

class SiteTwitterProfile(models.Model):
  site = models.OneToOneField(core_models.KegbotSite, related_name='twitter_profile')
  twitter_name = models.CharField(max_length=32)
  twitter_id = models.PositiveIntegerField()
  oauth_token = models.CharField(max_length=80)
  oauth_token_secret = models.CharField(max_length=80)
  enabled = models.BooleanField(default=False)

  def is_enabled(self):
    disabled = (not self.enabled or not self.twitter_name or not self.twitter_id or
      not self.oauth_token or not self.oauth_token_secret)
    return not disabled

class SiteTwitterSettings(_SettingsMixin):
  profile = models.OneToOneField(SiteTwitterProfile, related_name='settings')
  post_unauthenticated = models.BooleanField(default=True,
      help_text='Whether to generate tweets for unauthenticated '
          '(guest) pours.')
  post_unlinked = models.BooleanField(default=True,
      help_text='Whether to generate tweets for authenticated pours '
          'with no linked Twitter account.  The tweet will include the '
          'Kegbot username of the user.')

### User-specific
from socialregistration import signals as sr_signals
from socialregistration.contrib.twitter.models import TwitterProfile

class TwitterSettings(_SettingsMixin):
  profile = models.OneToOneField(TwitterProfile, unique=True,
      related_name='settings')
  twitter_name = models.CharField(max_length=64,
      help_text='Stores the twitter name of this user.')

def _twitter_connect_handler(sender, user, profile, client, request=None, **kwargs):
  settings, _ = TwitterSettings.objects.get_or_create(profile=profile)
  settings.twitter_name = client.get_user_info()['screen_name']
  settings.save()

sr_signals.connect.connect(_twitter_connect_handler, sender=TwitterProfile,
    dispatch_uid = 'twitter.connect')

