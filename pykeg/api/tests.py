import base64

from django.test import TestCase
from rest_framework.test import APIClient

from pykeg.core import models


class ApiClient:
    def __init__(self, api_key=None):
        self.client = APIClient()
        self.api_key = api_key

    def add_auth(self):
        if self.api_key:
            credentials = f"api:{self.api_key}"
            base64_credentials = base64.b64encode(credentials.encode()).decode()
            print("credentials", base64_credentials)
            self.client.credentials(HTTP_AUTHORIZATION=f"Basic {base64_credentials}")
        else:
            self.client.credentials()

    def get(self, *args, **kwargs):
        self.add_auth()
        response = self.client.get(*args, **kwargs)
        return response.status_code, response.json()

    def get_events(self):
        return self.get("/api/v2/events")


class V2ApiTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
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
