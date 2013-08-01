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

import datetime
from django.utils import timezone
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.conf.urls import patterns
from django.conf.urls import url
from django.conf import settings

from . import plugin

MAX_TASK_AGE = datetime.timedelta(hours=1)

_CACHED_PLUGINS = None

def get_plugin_class(name):
    try:
        module_path, member_name = name.rsplit(".", 1)
        module = import_module(module_path)
        cls = getattr(module, member_name)
    except (ValueError, ImportError, AttributeError), e:
        raise ImproperlyConfigured("Could not import plugin %s: %s" % (name, e))

    if not issubclass(cls, plugin.Plugin):
        raise ImproperlyConfigured('%s does not subclass plugin.Plugin', name)

    return cls

def get_plugins():
    global _CACHED_PLUGINS
    if _CACHED_PLUGINS is None:
        plugin_names = getattr(settings, 'KEGBOT_PLUGINS', [])
        plugins = []
        for name in plugin_names:
            cls = get_plugin_class(name)
            datastore = plugin.PluginDatastore(cls.get_short_name())
            plugin_obj = cls(datastore)
            plugins.append(plugin_obj)
        _CACHED_PLUGINS = plugins
    return _CACHED_PLUGINS

def get_admin_urls():
    urls = []
    for plugin in get_plugins():
        urls += _to_urls(plugin.get_extra_admin_views(), plugin.get_short_name())
    return patterns('', *urls)

def get_account_urls():
    urls = []
    for plugin in get_plugins():
        urls += _to_urls(plugin.get_extra_user_views(), plugin.get_short_name())
    return patterns('', *urls)

def _to_urls(urllist, short_name):
    urls = []
    for regex, fn, viewname in urllist:
        regex = 'plugin/%s/%s' % (short_name, regex)
        viewname = 'plugin-%s-%s' % (short_name, viewname)
        urls.append(url(regex, fn, name=viewname))
    return urls

def is_stale(time, now=None):
    if not now:
        now = timezone.now()
    return (time + MAX_TASK_AGE) <= now

def get_logger(name):
    try:
        from celery.utils.log import get_task_logger
        logger = get_task_logger(name)
    except ImportError:
        import logging
        logger = logging.getLogger(name)
    return logger
