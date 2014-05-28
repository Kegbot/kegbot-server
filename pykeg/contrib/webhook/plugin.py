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

"""Webhook plugin for Kegbot."""

from pykeg.core.util import SuppressTaskErrors
from pykeg.plugin import plugin
from pykeg.proto import protolib

from . import forms
from . import tasks
from . import views

KEY_SITE_SETTINGS = 'settings'


class WebhookPlugin(plugin.Plugin):
    NAME = 'Web Hooks'
    SHORT_NAME = 'webhook'
    DESCRIPTION = 'Posts each system event to configured URLs'
    URL = 'http://kegbot.org'
    VERSION = '1.0.0'

    def get_admin_settings_view(self):
        return views.admin_settings

    def handle_new_events(self, events):
        for event in events:
            self.handle_event(event)

    def handle_event(self, event):
        self.logger.info('Handling new event: %s' % event.id)
        settings = self.get_site_settings()
        urls = settings.get('webhook_urls', '').strip().split()
        event_dict = protolib.ToDict(event, full=True)
        for url in urls:
            with SuppressTaskErrors(self.logger):
                tasks.webhook_post.delay(url, event_dict)

    ### Webhook-specific methods

    def get_site_settings_form(self):
        return self.datastore.load_form(forms.SiteSettingsForm, KEY_SITE_SETTINGS)

    def get_site_settings(self):
        return self.get_site_settings_form().initial

    def save_site_settings_form(self, form):
        self.datastore.save_form(form, KEY_SITE_SETTINGS)
