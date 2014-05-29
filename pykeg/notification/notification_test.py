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

"""Unittests for notification module."""

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from pykeg.backend import get_kegbot_backend
from pykeg.core import models
from pykeg.core import defaults

from pykeg import notification
from pykeg.notification.backends.base import BaseNotificationBackend


class TestBackendA(BaseNotificationBackend):
    def notify(self, event, user):
        pass


class TestBackendB(BaseNotificationBackend):
    def notify(self, event, user):
        pass


class StandaloneNotificationTestCase(TestCase):
    """Standalone notification tests, no other components involved."""

    @override_settings(NOTIFICATION_BACKENDS=[
        'pykeg.notification.notification_test.TestBackendA',
        'pykeg.notification.notification_test.TestBackendB',
    ])
    def test_get_backends(self):
        backends = notification.get_backends()
        self.assertEquals(2, len(backends))
        self.assertIsInstance(backends[0], TestBackendA, 'Expected TestBackendA obj')
        self.assertIsInstance(backends[1], TestBackendB, 'Expected TestBackendB obj')

    @override_settings(NOTIFICATION_BACKENDS=['pykeg.bougus.NoBackend'])
    def test_improperly_configured(self):
        self.assertRaises(ImproperlyConfigured, notification.get_backends)


class NotificationTestCase(TestCase):
    def setUp(self):
        self.backend = get_kegbot_backend()
        defaults.set_defaults(set_is_setup=True)

        self.user = models.User.objects.create(username='notification_user',
            email='test@example')

    @override_settings(NOTIFICATION_BACKENDS=['pykeg.notification.notification_test.CaptureBackend'])
    def test_notifications(self):
        class CaptureBackend(BaseNotificationBackend):
            """Notification backend which captures calls."""
            captured = []

            def notify(self, event, user):
                self.captured.append((event, user))

        SystemEvent = models.SystemEvent

        backends = [CaptureBackend()]
        captured = CaptureBackend.captured
        self.assertEquals(0, len(captured))

        prefs = models.NotificationSettings.objects.create(user=self.user,
            backend='pykeg.notification.notification_test.CaptureBackend',
            keg_tapped=False, session_started=False, keg_volume_low=False,
            keg_ended=False)

        event = SystemEvent(kind=SystemEvent.KEG_TAPPED)
        notification.handle_single_event(event, backends)
        self.assertEquals(0, len(captured))
        prefs.keg_tapped = True
        prefs.save()
        notification.handle_single_event(event, backends)
        self.assertEquals(1, len(captured))
        del captured[:]

        event = SystemEvent(kind=SystemEvent.SESSION_STARTED)
        notification.handle_single_event(event, backends)
        self.assertEquals(0, len(captured))
        prefs.session_started = True
        prefs.save()
        notification.handle_single_event(event, backends)
        self.assertEquals(1, len(captured))
        del captured[:]

        event = SystemEvent(kind=SystemEvent.KEG_ENDED)
        notification.handle_single_event(event, backends)
        self.assertEquals(0, len(captured))
        prefs.keg_ended = True
        prefs.save()
        notification.handle_single_event(event, backends)
        self.assertEquals(1, len(captured))
        del captured[:]

        event = SystemEvent(kind=SystemEvent.KEG_VOLUME_LOW)
        notification.handle_single_event(event, backends)
        self.assertEquals(0, len(captured))
        prefs.keg_volume_low = True
        prefs.save()
        notification.handle_single_event(event, backends)
        self.assertEquals(1, len(captured))
        del captured[:]
