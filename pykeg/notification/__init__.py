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

from __future__ import absolute_import

import logging
logger = logging.getLogger('notification')

from django.conf import settings
from django.utils.module_loading import import_by_path

__all__ = ['get_backends', 'handle_new_system_events']


def get_backends():
    """Returns the enabled notification backend(s)."""
    backend_names = settings.NOTIFICATION_BACKENDS
    backends = [import_by_path(n)() for n in backend_names]
    return backends


def handle_new_system_events(events):
    """Processes newly-generated system events.

    Args:
        events: an iterable of models.SystemEvent objects

    Returns:
        None
    """
    backends = get_backends()
    logger.info('Handling %s event(s)' % len(events))
    logger.info('Num backends: %s' % len(backends))
    for event in events:
        handle_single_event(event, backends)


def handle_single_event(event, backends):
    from pykeg.core import models as core_models
    kind = event.kind
    logger.info('Processing event: %s' % event.kind)

    for backend in backends:
        backend_name = str(backend.__class__)
        prefs = core_models.NotificationSettings.objects.filter(backend=backend_name)

        if kind == event.KEG_TAPPED:
            prefs = prefs.filter(keg_tapped=True)
        elif kind == event.SESSION_STARTED:
            prefs = prefs.filter(session_started=True)
        elif kind == event.KEG_VOLUME_LOW:
            prefs = prefs.filter(keg_volume_low=True)
        elif kind == event.KEG_ENDED:
            prefs = prefs.filter(keg_ended=True)
        else:
            logger.info('Unknown kind: %s' % kind)
            prefs = []

        logger.debug('Matching prefs: %s' % str(prefs))
        for matching_pref in prefs:
            user = matching_pref.user
            logger.info('Notifying %s for event %s' % (user, kind))
            backend.notify(event, user)
