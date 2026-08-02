"""Unittests for setup wizard."""

from django.core.cache import cache
from django.test import TransactionTestCase
from django.test.utils import override_settings
from django.urls import reverse

from pykeg.core import defaults, models


class SetupWizardTestCase(TransactionTestCase):
    def setUp(self):
        cache.clear()

    def test_settings_debug_false(self):
        """Verify wizard is not offered (DEBUG is False)."""
        for path in ("/", "/stats/"):
            response = self.client.get(path)
            self.assertContains(response, "<h2>Kegbot Offline</h2>", status_code=403)
            self.assertNotContains(response, "Start Setup", status_code=403)

        response = self.client.get("/setup/")
        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=True)
    def test_settings_debug_true(self):
        """Verify wizard is offered (DEBUG is True)."""
        for path in ("/", "/stats/"):
            response = self.client.get(path)
            self.assertContains(response, "<h2>Setup Required</h2>", status_code=403)
            self.assertContains(response, "Start Setup", status_code=403)

        response = self.client.get("/setup/")
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_admin_step_logs_in_new_admin(self):
        """The admin-user step creates the admin and logs them in."""
        defaults.set_defaults()  # site exists but is not yet set up

        response = self.client.post(
            reverse("setup_admin"),
            {
                "username": "wizadmin",
                "email": "admin@example.com",
                "password": "s3cret-pass",
                "confirm_password": "s3cret-pass",
            },
        )
        self.assertRedirects(response, reverse("setup_finish"), fetch_redirect_response=False)

        admin = models.User.objects.get(username="wizadmin")
        self.assertTrue(admin.is_superuser)
        # The freshly-created admin should now be authenticated.
        self.assertEqual(str(admin.pk), self.client.session.get("_auth_user_id"))

    def test_setup_not_shown(self):
        """Verify wizard is not shown on set-up site."""
        site = defaults.set_defaults()
        site.is_setup = True
        site.save()
        for path in ("/", "/stats/"):
            response = self.client.get(path)
            self.assertNotContains(response, "<h2>Kegbot Offline</h2>", status_code=200)
            self.assertNotContains(response, "<h2>Setup Required</h2>", status_code=200)
            self.assertNotContains(response, "Start Setup", status_code=200)

        response = self.client.get("/setup/")
        self.assertEqual(response.status_code, 404)
