# Copyright 2013 Mike Wakerly <opensource@hoho.com>
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

"""Plugin interface for extending the Kegbot frontend."""

import logging
from pykeg.plugin import models
from kegbot.util.util import AttrDict

class PluginDatastore:
    """Interface for plugins to persist plugin-specific data."""

    def __init__(self, plugin_name):
        self.plugin_name = plugin_name

    def set(self, key, value):
        """Store plugin-specific data."""
        if value is None:
            self.delete(key)
            return
        try:
            row = models.PluginData.objects.get(plugin_name=self.plugin_name, key=key)
            row.value = value
            row.save()
        except models.PluginData.DoesNotExist:
            models.PluginData.objects.create(plugin_name=self.plugin_name, key=key,
                value=value)

    def get(self, key, default=None):
        """Fetch plugin-specific data."""
        try:
            row = models.PluginData.objects.get(plugin_name=self.plugin_name,
                key=key)
            return row.value
        except models.PluginData.DoesNotExist:
            return default

    def delete(self, key):
        try:
            models.PluginData.objects.get(plugin_name=self.plugin_name,
                key=key).delete()
        except models.PluginData.DoesNotExist:
            pass

class Plugin:
    """Interface class for plugins."""

    NAME = None
    SHORT_NAME = None
    DESCRIPTION = None
    VERSION = None
    URL = None

    def __init__(self, datastore):
        self.datastore = datastore
        self.logger = logging.getLogger(self.SHORT_NAME)

    @classmethod
    def get_version(cls):
        """Return the curent plugin version.

        Subclasses should set the class attribute VERSION, which is
        returned by the default implementation.

        Returns:
            The version, as a tuple of (major, minor, micro[, tag]).
            Major, minor, and micro must be integers; tag, if present,
            must be an arbitrary string.
        """
        if not cls.VERSION:
            raise NotImplementedError
        return cls.VERSION

    @classmethod
    def get_name(cls):
        """Return a human-readable (one or two word) name for this plugin.

        Subclasses should set the class attribute NAME, which is
        returned by the default implementation.
        """
        if not cls.NAME:
            raise NotImplementedError
        return cls.NAME

    @classmethod
    def get_short_name(cls):
        """Return a short for this plugin.

        Subclasses should set the class attribute NAME, which is
        returned by the default implementation.
        """
        if not cls.SHORT_NAME:
            raise NotImplementedError
        return cls.SHORT_NAME

    @classmethod
    def get_description(cls):
        """Return a concise human-readable description for this plugin.

        Subclasses should set the class attribute DESCRIPTION, which is
        returned by the default implementation.
        """
        if not cls.DESCRIPTION:
            raise NotImplementedError
        return cls.DESCRIPTION

    @classmethod
    def get_url(cls):
        """Returns the information URL (homepage) for the plugin.

        Subclassses should set the class attribute URL, which is returned
        by the default implementation.
        """
        if not cls.URL:
            raise NotImplementedError
        return cls.URL

    ### Plugin methods

    def get_admin_settings_view(self):
        """Returns the view instance for the main admin settings for this
        plugin, or None.
        """
        return None

    def get_extra_admin_views(self):
        """Returns an iterable of additional views to be installed in the admin
        site section this plugin.

        Each item should be a 3-tuple of the form:
          (regex, view name, url name)

        Each view will be installed with the name
        "plugin-<plugin name>-<url name>"
        """
        return []

    def get_user_settings_view(self):
        """Returns the view instance for the main user settings for this
        plugin, or None.
        """
        return None

    def get_extra_user_views(self):
        """Returns an iterable of additional views to be installed in the
        user section for this plugin.

        Each item should be a 3-tuple of the form:
          (regex, view name, url name)

        Each view will be installed with the name
        "plugin-<plugin name>-<url name>"
        """
        return []

    def handle_new_event(self, event):
        """Called synchronously when a new event is posted.

        Plugins should *quickly* perform any work. Long-running work can be
        performed by scheduling a background task in this method."""
        pass

    ### Helpers

    def save_form(self, form, prefix):
        """Helper method to save a form using the specified per-field prefix."""
        for field_name, value in form.cleaned_data.iteritems():
            self.datastore.set('%s:%s' % (prefix, field_name), value)

    def get_saved_form_data(self, form, prefix):
        """Helper method to load a form using the specified per-field prefix."""
        ret = {}
        for field_name, field in form.fields.iteritems():
            initial = self.datastore.get('%s:%s' % (prefix, field_name))
            if initial is not None:
                ret[field_name] = field.to_python(initial)
        return AttrDict(ret)

    def load_form_defaults(self, form, prefix):
        """Applies defaults to a form using `get_saved_form_data`."""
        defaults = self.get_saved_form_data(form, prefix)
        for field_name, value in defaults.iteritems():
            form.fields[field_name].initial = value
        return form
