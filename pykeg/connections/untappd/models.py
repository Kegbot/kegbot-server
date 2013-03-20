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


from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from socialregistration.signals import connect

class UntappdProfile(models.Model):
  user = models.ForeignKey(User, unique=True)
  site = models.ForeignKey(Site, default=Site.objects.get_current)
  untappd = models.CharField(max_length=255)

  def __unicode__(self):
    try:
      return u'%s: %s' % (self.user, self.untappd)
    except User.DoesNotExist:
      return u'None'

  def authenticate(self):
    return authenticate(untappd=self.untappd)

class UntappdAccessToken(models.Model):
  profile = models.OneToOneField(UntappdProfile, related_name='access_token')
  access_token = models.CharField(max_length=255)

def save_untappd_token(sender, user, profile, client, **kwargs):
  try:
    UntappdAccessToken.objects.get(profile=profile).delete()
  except UntappdAccessToken.DoesNotExist:
    pass

  UntappdAccessToken.objects.create(access_token=client.get_access_token(),
      profile=profile)

connect.connect(save_untappd_token, sender=UntappdProfile,
    dispatch_uid='pykeg_connect_untappd_token')
