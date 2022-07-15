"""Unittests for registration functions."""

from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

from pykeg.core import defaults
from pykeg.core import models as core_models


class ForgotPasswordTest(TestCase):
    def setUp(self):
        defaults.set_defaults(set_is_setup=True)

        self.user = core_models.User.objects.create(
            username="notification_user", email="test@example.com"
        )

        # Password reset requires a usable password.
        self.user.set_password("1234")
        self.user.save()

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    @override_settings(DEFAULT_FROM_EMAIL="test-from@example")
    def test_notifications(self):
        response = self.client.get("/accounts/password/reset/")
        self.assertContains(response, "Reset Password", status_code=200)
        self.assertEqual(0, len(mail.outbox))

        response = self.client.post(
            "/accounts/password/reset/", data={"email": "test@example.com"}, follow=True
        )
        self.assertContains(response, "E-Mail Sent", status_code=200)
        self.assertEqual(1, len(mail.outbox))

        msg = mail.outbox[0]

        # TODO(mikey): Customize subject with `kbsite.title`
        self.assertEqual("Password reset", msg.subject)
        self.assertEqual(["test@example.com"], msg.to)
        self.assertEqual("test-from@example", msg.from_email)
