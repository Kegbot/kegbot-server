#!/usr/bin/env python
#
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

from django import forms

from . import models

class TwitterSettingsForm(forms.ModelForm):
  class Meta:
    model = models.TwitterSettings
    fields = ('enabled', 'post_session_joined', 'post_drink_poured')

class SiteTwitterSettingsForm(forms.ModelForm):
  class Meta:
    model = models.SiteTwitterSettings
    fields = ('enabled', 'post_session_joined', 'post_drink_poured',
        'post_unauthenticated', 'post_unlinked')

class UnlinkTwitterForm(forms.Form):
  pass
