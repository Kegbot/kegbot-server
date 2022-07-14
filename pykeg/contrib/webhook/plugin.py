"""Webhook plugin for Kegbot."""

from pykeg.core.util import SuppressTaskErrors
from pykeg.plugin import plugin
from pykeg.proto import protolib

from . import forms, tasks, views

KEY_SITE_SETTINGS = "settings"


class WebhookPlugin(plugin.Plugin):
    NAME = "Web Hooks"
    SHORT_NAME = "webhook"
    DESCRIPTION = "Posts each system event to configured URLs"
    URL = "http://kegbot.org"
    VERSION = "1.0.0"

    def get_admin_settings_view(self):
        return views.admin_settings

    def handle_new_events(self, events):
        for event in events:
            self.handle_event(event)

    def handle_event(self, event):
        self.logger.info("Handling new event: %s" % event.id)
        settings = self.get_site_settings()
        urls = settings.get("webhook_urls", "").strip().split()
        event_dict = protolib.ToDict(event, full=True)
        for url in urls:
            with SuppressTaskErrors(self.logger):
                tasks.webhook_post.delay(url, event_dict)

    # Webhook-specific methods

    def get_site_settings_form(self):
        return self.datastore.load_form(forms.SiteSettingsForm, KEY_SITE_SETTINGS)

    def get_site_settings(self):
        return self.get_site_settings_form().initial

    def save_site_settings_form(self, form):
        self.datastore.save_form(form, KEY_SITE_SETTINGS)
