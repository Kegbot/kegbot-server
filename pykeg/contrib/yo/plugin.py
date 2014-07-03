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

from . import forms
from . import tasks
from . import views

class YoPlugin(plugin.Plugin):
    NAME = 'Yo'
    SHORT_NAME = 'yo'
    DESCRIPTION = 'Each drinking system event sends a yo'
    URL = 'http://kegbot.org'
    VERSION = '1.0.0'

    def get_admin_settings_view(self):
        return views.admin_settings

    def handle_new_events(self, events):
        for event in events:
            self.handle_event(event)

    def handle_event(self, event):
        if event.kind != event.DRINK_POURED:
            self.logger.info('Ignoring event: %s' % event.kind)
            return

        settings = self.get_site_settings()
        api_token = settings.get('api_token', '').strip()
        if not api_token:
            self.logger.info('Ignoring event: %s because there is no yo api_token' % event.id)
            return
		
        self.logger.info('Handling new event: %s' % event.id)
        with SuppressTaskErrors(self.logger):
            tasks.yo_post.delay(api_token)

    def get_site_settings_form(self):
        return self.datastore.load_form(forms.YoSettingsForm, "yoSettings")

    def get_site_settings(self):
        return self.get_site_settings_form().initial

    def save_site_settings_form(self, form):
        self.datastore.save_form(form, "yoSettings")
