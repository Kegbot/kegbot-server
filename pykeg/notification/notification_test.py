"""Unittests for notification module."""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from pykeg.backend import get_kegbot_backend
from pykeg.core import models
from pykeg.core import defaults

from pykeg import notification
from pykeg.notification.backends.base import BaseNotificationBackend


class TestBackendA(BaseNotificationBackend):
    @classmethod
    def name(cls):
        return "pykeg.notification.test.TestBackendA"

    def notify(self, event, user):
        pass


class TestBackendB(BaseNotificationBackend):
    @classmethod
    def name(cls):
        return "pykeg.notification.test.TestBackendB"

    def notify(self, event, user):
        pass


class StandaloneNotificationTestCase(TestCase):
    """Standalone notification tests, no other components involved."""

    @override_settings(
        NOTIFICATION_BACKENDS=[
            "pykeg.notification.notification_test.TestBackendA",
            "pykeg.notification.notification_test.TestBackendB",
        ]
    )
    def test_get_backends(self):
        backends = notification.get_backends()
        self.assertEqual(2, len(backends))
        self.assertIsInstance(backends[0], TestBackendA, "Expected TestBackendA obj")
        self.assertIsInstance(backends[1], TestBackendB, "Expected TestBackendB obj")

    @override_settings(NOTIFICATION_BACKENDS=["pykeg.bougus.NoBackend"])
    def test_improperly_configured(self):
        self.assertRaises(ImproperlyConfigured, notification.get_backends)


class NotificationTestCase(TestCase):
    def setUp(self):
        self.backend = get_kegbot_backend()
        defaults.set_defaults(set_is_setup=True)

        self.user = models.User.objects.create(username="notification_user", email="test@example")

    @override_settings(
        NOTIFICATION_BACKENDS=["pykeg.notification.notification_test.CaptureBackend"]
    )
    def test_notifications(self):
        class CaptureBackend(BaseNotificationBackend):
            """Notification backend which captures calls."""

            captured = []

            @classmethod
            def name(cls):
                return "CaptureBackend"

            def notify(self, event, user):
                self.captured.append((event, user))

        SystemEvent = models.SystemEvent

        backends = [CaptureBackend()]
        captured = CaptureBackend.captured
        self.assertEqual(0, len(captured))

        prefs = models.NotificationSettings.objects.create(
            user=self.user,
            backend=CaptureBackend.name(),
            keg_tapped=False,
            session_started=False,
            keg_volume_low=False,
            keg_ended=False,
        )

        event = SystemEvent(kind=SystemEvent.KEG_TAPPED)
        notification.handle_single_event(event, backends)
        self.assertEqual(0, len(captured))
        prefs.keg_tapped = True
        prefs.save()
        notification.handle_single_event(event, backends)
        self.assertEqual(1, len(captured))
        del captured[:]

        event = SystemEvent(kind=SystemEvent.SESSION_STARTED)
        notification.handle_single_event(event, backends)
        self.assertEqual(0, len(captured))
        prefs.session_started = True
        prefs.save()
        notification.handle_single_event(event, backends)
        self.assertEqual(1, len(captured))
        del captured[:]

        event = SystemEvent(kind=SystemEvent.KEG_ENDED)
        notification.handle_single_event(event, backends)
        self.assertEqual(0, len(captured))
        prefs.keg_ended = True
        prefs.save()
        notification.handle_single_event(event, backends)
        self.assertEqual(1, len(captured))
        del captured[:]

        event = SystemEvent(kind=SystemEvent.KEG_VOLUME_LOW)
        notification.handle_single_event(event, backends)
        self.assertEqual(0, len(captured))
        prefs.keg_volume_low = True
        prefs.save()
        notification.handle_single_event(event, backends)
        self.assertEqual(1, len(captured))
        del captured[:]
