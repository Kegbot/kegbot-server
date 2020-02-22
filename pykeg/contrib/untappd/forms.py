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

"""Untappd plugin forms."""

from django import forms

WIDE_TEXT = forms.TextInput(attrs={'class': 'input-block-level'})


class SiteSettingsForm(forms.Form):
    client_id = forms.CharField(required=False, widget=WIDE_TEXT,
                                help_text='Untappd API Client ID.')
    client_secret = forms.CharField(required=False, widget=WIDE_TEXT,
                                    help_text='Untappd API Client Secret')


class UserSettingsForm(forms.Form):
    enable_checkins = forms.BooleanField(initial=True, required=False,
                                         help_text='Check in when you join a session.')
