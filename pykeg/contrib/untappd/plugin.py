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

"""Untappd plugin for Kegbot."""

from django.conf import settings
from django.utils import timezone
from pykeg.core.util import SuppressTaskErrors
from pykeg.plugin import plugin
from pykeg.plugin import util as plugin_util

from . import forms
from . import tasks
from . import views

KEY_SITE_SETTINGS = 'settings'
KEY_CLIENT_ID = 'client_id'
KEY_CLIENT_SECRET = 'client_secret'


class UntappdPlugin(plugin.Plugin):
    NAME = 'Untappd'
    SHORT_NAME = 'untappd'
    DESCRIPTION = 'Check in when you pour!'
    URL = 'http://kegbot.org'
    VERSION = '0.0.1-pre'

    def get_admin_settings_view(self):
        if settings.EMBEDDED:
            return None
        return views.admin_settings

    def get_user_settings_view(self):
        return views.user_settings

    def get_extra_user_views(self):
        return [
            ('redirect/$', 'pykeg.contrib.untappd.views.auth_redirect', 'redirect'),
            ('callback/$', 'pykeg.contrib.untappd.views.auth_callback', 'callback'),
        ]

    def handle_new_events(self, events):
        for event in events:
            self.handle_event(event)

    def handle_event(self, event):
        self.logger.info('Handling new event: %s' % event)
        user = event.user

        if event.kind != event.DRINK_POURED:
            self.logger.info('Ignoring event: %s' % event.kind)
            return

        if user.is_guest():
            self.logger.info('Ignoring event: anonymous.')
            return

        if plugin_util.is_stale(event.time):
            self.logger.info('Ignoring event: stale.')
            return

        token = self.get_user_token(user)
        if not token:
            self.logger.info('Ignoring event: no token for user %s.' % user.username)
            return

        settings = self.get_user_settings(user)
        if not settings or not settings.get('enable_checkins'):
            self.logger.info('Ignoring event: not enabled.')
            return

        beer_id = event.drink.keg.type.untappd_beer_id
        if not beer_id:
            self.logger.info('Ignoring event: no untappd beer id.')
            return

        shout = None
        if event.drink.shout:
            shout = event.drink.shout

        foursquare_venue_id = foursquare_client_id = foursquare_client_secret = None
        foursquare = self.plugin_registry.get('foursquare')
        if foursquare:
            foursquare_client_id, foursquare_client_secret = foursquare.get_credentials()
            foursquare_venue_id = foursquare.get_venue_id()
            if foursquare_venue_id:
                self.logger.info('Adding location info, foursquare venue id: {}'.format(foursquare_venue_id))
            else:
                self.logger.info('No Foursquare venue id, not adding location info.')
        else:
            self.logger.info('Foursquare not available, not adding location info.')

        timezone_name = timezone.get_current_timezone_name()

        with SuppressTaskErrors(self.logger):
            tasks.untappd_checkin.delay(token, beer_id, timezone_name, shout=shout,
                foursquare_client_id=foursquare_client_id,
                foursquare_client_secret=foursquare_client_secret,
                foursquare_venue_id=foursquare_venue_id)

    ### Untappd-specific methods

    def get_credentials(self):
        if settings.EMBEDDED:
            return (
                getattr(settings, 'UNTAPPD_CLIENT_ID', ''),
                getattr(settings, 'UNTAPPD_CLIENT_SECRET', ''),
            )
        data = self.get_site_settings()
        return data.get('client_id'), data.get('client_secret')

    def get_site_settings_form(self):
        return self.datastore.load_form(forms.SiteSettingsForm, KEY_SITE_SETTINGS)

    def get_site_settings(self):
        return self.get_site_settings_form().initial

    def save_site_settings_form(self, form):
        self.datastore.save_form(form, KEY_SITE_SETTINGS)

    def get_user_settings_form(self, user):
        return self.datastore.load_form(forms.UserSettingsForm, 'user_settings:%s' % user.id)

    def get_user_settings(self, user):
        return self.get_user_settings_form(user).initial

    def save_user_settings_form(self, user, form):
        self.datastore.save_form(form, 'user_settings:%s' % user.id)

    def get_user_profile(self, user):
        return self.datastore.get('user_detail:%s' % user.id, {})

    def save_user_profile(self, user, profile):
        self.datastore.set('user_detail:%s' % user.id, profile)

    def get_user_token(self, user):
        return self.datastore.get('user_token:%s' % user.id)

    def save_user_token(self, user, token):
        self.datastore.set('user_token:%s' % user.id, token)
