import base64

from django.test import TestCase
from rest_framework.test import APIClient

from pykeg.core import models
from pykeg.core.util import get_version


class ApiClient:
    def __init__(self, api_key=None):
        self.client = APIClient()
        self.api_key = api_key

    def add_auth(self):
        if self.api_key:
            credentials = f"api:{self.api_key}"
            base64_credentials = base64.b64encode(credentials.encode()).decode()
            self.client.credentials(HTTP_AUTHORIZATION=f"Basic {base64_credentials}")
        else:
            self.client.credentials()

    def get(self, *args, **kwargs):
        self.add_auth()
        response = self.client.get(*args, **kwargs)
        return response.status_code, response.json()

    def get_events(self):
        return self.get("/api/events")


class V2ApiTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        # The fixture bakes in an older server_version; keep it current so the
        # "upgrade required" gate doesn't intercept API requests under test.
        self.site.server_version = get_version()
        self.site.save()
        self.user = models.User.objects.all().first()
        self.api_key = models.ApiKey.objects.get_or_create(user=self.user)[0]

    def test_get_events(self):
        status, data = self.client.get_events()
        self.assertEqual(200, status)
        events = data["results"]
        self.assertEqual(10, len(events))
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])

    def test_locked_down_site_prevents_api_access(self):
        """Verify that an API key is required when privacy is non-public."""
        self.assertEqual(models.KegbotSite.PRIVACY_CHOICE_PUBLIC, self.site.privacy)
        status, _ = self.client.get_events()
        self.assertEqual(200, status)

        # Lock down into members-only. Confirm 403.
        self.site.privacy = models.KegbotSite.PRIVACY_CHOICE_MEMBERS
        self.site.save()
        status, _ = self.client.get_events()
        self.assertEqual(403, status)

        # Start providing an API key. Confirm 200.
        self.client.api_key = self.api_key.key
        status, _ = self.client.get_events()
        self.assertEqual(200, status)

        # Lock down to staff only. Confirm 403 again.
        self.site.privacy = models.KegbotSite.PRIVACY_CHOICE_STAFF
        self.site.save()
        status, _ = self.client.get_events()
        self.assertEqual(403, status)

        # Promote our user to staff. Confirm 200 again.
        self.user.is_staff = True
        self.user.save()
        status, _ = self.client.get_events()
        self.assertEqual(200, status)

    def test_deactivated_api_key_is_rejected(self):
        """Verify that deactivated API keys are rejected."""
        # Put site into members-only mode.
        self.site.privacy = models.KegbotSite.PRIVACY_CHOICE_MEMBERS
        self.site.save()
        status, _ = self.client.get_events()
        self.assertEqual(403, status)

        # Confirm API key is working before we deactivate the key.
        self.client.api_key = self.api_key.key
        status, _ = self.client.get_events()
        self.assertEqual(200, status)

        # Deactivate the key. Confirm 403.
        self.api_key.active = False
        self.api_key.save()
        status, _ = self.client.get_events()
        self.assertEqual(403, status)

    def test_api_key_from_inactive_account_is_rejected(self):
        """Verify that API keys from deactivated users are appropriately rejected."""
        # Put site into members-only mode.
        self.site.privacy = models.KegbotSite.PRIVACY_CHOICE_MEMBERS
        self.site.save()
        status, _ = self.client.get_events()
        self.assertEqual(403, status)

        # Confirm API key is working before we deactivate the user.
        self.client.api_key = self.api_key.key
        status, _ = self.client.get_events()
        self.assertEqual(200, status)

        # Deactivate the user. Confirm 403.
        self.user.is_active = False
        self.user.save()
        status, _ = self.client.get_events()
        self.assertEqual(403, status)


class V2ApiPermissionsTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()
        self.member = models.User.objects.get(username="alice")
        self.member_key = models.ApiKey.objects.get_or_create(user=self.member)[0]

    def test_users_are_read_only(self):
        self.client.api_key = self.member_key.key
        self.client.add_auth()
        response = self.client.client.patch(
            f"/api/users/{self.member.id}", {"display_name": "hax"}, format="json"
        )
        self.assertEqual(405, response.status_code)

    def test_plugin_data_requires_admin(self):
        self.client.api_key = self.member_key.key
        status, _ = self.client.get("/api/plugin-data")
        self.assertEqual(403, status)

    def test_beverages_require_admin_to_write(self):
        self.client.api_key = self.member_key.key
        self.client.add_auth()
        response = self.client.client.post("/api/beverages", {"name": "Nope"}, format="json")
        self.assertEqual(403, response.status_code)

    def test_notification_settings_are_scoped_to_caller(self):
        other = models.User.objects.get(username="bob")
        models.NotificationSettings.objects.create(user=other, backend="test", keg_tapped=True)
        self.client.api_key = self.member_key.key
        status, data = self.client.get("/api/notification-settings")
        self.assertEqual(200, status)
        self.assertEqual([], data["results"])


class SchemaTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        site = models.KegbotSite.objects.all().first()
        site.server_version = get_version()
        site.save()

    def test_schema(self):
        response = self.client.get("/api/schema")
        self.assertEqual(200, response.status_code)
        self.assertIn("openapi", response.headers["Content-Type"])

    def test_docs(self):
        response = self.client.get("/api/docs")
        self.assertEqual(200, response.status_code)
