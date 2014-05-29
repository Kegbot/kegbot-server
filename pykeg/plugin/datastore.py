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

"""Data storage interface and implementations for plugins."""

from kegbot.util.util import AttrDict
from pykeg.core import models


class PluginDatastore(object):
    """Interface for plugins to persist plugin-specific data."""

    def __init__(self, plugin_name):
        self.plugin_name = plugin_name

    def set(self, key, value):
        """Store plugin-specific data."""
        raise NotImplementedError

    def get(self, key, default=None):
        """Fetch plugin-specific data."""
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def save_form(self, form, prefix):
        """Helper method to save a form using the specified per-field prefix."""
        for field_name, value in form.cleaned_data.iteritems():
            self.set('%s:%s' % (prefix, field_name), value)

    def load_form(self, form_cls, prefix, form_kwargs={}):
        """Helper method to load a form using the specified per-field prefix."""
        data = AttrDict()
        for field_name, field in form_cls.base_fields.iteritems():
            initial = self.get('%s:%s' % (prefix, field_name))
            if initial is not None:
                data[field_name] = field.to_python(initial)
            else:
                if field.initial is not None:
                    data[field_name] = field.initial
        return form_cls(initial=data, **form_kwargs)


class ModelDatastore(PluginDatastore):
    """PluginDatastore backed by models.PluginData rows."""

    def set(self, key, value):
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


class InMemoryDatastore(PluginDatastore):
    def __init__(self, *args, **kwargs):
        super(InMemoryDatastore, self).__init__(*args, **kwargs)
        self.data = {}

    def _keyname(self, key):
        """Returns the datastore-namespaced key name."""
        return '{}:{}'.format(self.plugin_name, key)

    def set(self, key, value):
        if value is None:
            self.delete(key)
        else:
            self.data[self._keyname(key)] = value

    def get(self, key, default=None):
        return self.data.get(self._keyname(key), default)

    def delete(self, key):
        keyname = self._keyname(key)
        if keyname in self.data:
            del self.data[keyname]
