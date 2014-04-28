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

"""Twitter plugin forms."""

from django import forms

WIDE_TEXT = forms.TextInput(attrs={'class': 'input-block-level'})


class CredentialsForm(forms.Form):
    consumer_key = forms.CharField(required=False)
    consumer_secret = forms.CharField(required=False)


class SiteSettingsForm(forms.Form):
    tweet_keg_events = forms.BooleanField(initial=True, required=False,
        help_text='Tweet when a keg is started or ended.')
    tweet_session_events = forms.BooleanField(initial=True, required=False,
        help_text='Tweet when a new session is started.')
    tweet_drink_events = forms.BooleanField(initial=False, required=False,
        help_text='Tweet whenever a drink is poured (caution: potentially annoying).')
    include_guests = forms.BooleanField(initial=True, required=False,
        help_text='When tweeting drink events, whether to include guest pours.')
    include_pictures = forms.BooleanField(initial=False, required=False,
        help_text='Attach photos to tweets when available?')
    append_url = forms.BooleanField(initial=True, required=False,
        help_text='Whether to append drink URLs to tweets.')
    keg_started_template = forms.CharField(max_length=255, widget=WIDE_TEXT,
        initial='Woot! Just tapped a new keg of $BEER!',
        help_text='Template to use when a new keg is tapped.')
    keg_ended_template = forms.CharField(max_length=255, widget=WIDE_TEXT,
        initial='The keg of $BEER has been finished.',
        help_text='Template to use when a keg is ended.')
    session_started_template = forms.CharField(max_length=255, widget=WIDE_TEXT,
        initial='$DRINKER kicked off a new session on $SITENAME.',
        help_text='Template to use when a session is started.')
    session_joined_template = forms.CharField(max_length=255, widget=WIDE_TEXT,
        initial='$DRINKER joined the session.',
        help_text='Template to use when a session is joined.')
    drink_poured_template = forms.CharField(max_length=255, widget=WIDE_TEXT,
        initial='$DRINKER poured $VOLUME of $BEER on $SITENAME.',
        help_text='Template to use when a drink is poured.')
    user_drink_poured_template = forms.CharField(max_length=255, widget=WIDE_TEXT,
        initial='Just poured $VOLUME of $BEER on $SITENAME. #kegbot',
        help_text='Template to use in user tweets when a drink is poured.')


class UserSettingsForm(forms.Form):
    tweet_session_events = forms.BooleanField(initial=True, required=False,
        help_text='Tweet when you join a session.')
    tweet_drink_events = forms.BooleanField(initial=False, required=False,
        help_text='Tweet every time you pour (caution: potentially annoying).')
    include_pictures = forms.BooleanField(initial=False, required=False,
        help_text='Attach photos to tweets when available?')


class SendTweetForm(forms.Form):
    tweet_custom = forms.CharField(max_length=140, widget=WIDE_TEXT,
        label='Tweet',
        help_text='Send a tweet from the Kegbot system account')
