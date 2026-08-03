import base64
import datetime

from django.test import TestCase
from django.utils import timezone
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
            f"/api/users/{self.member.username}", {"display_name": "hax"}, format="json"
        )
        self.assertEqual(405, response.status_code)

    def test_user_detail_is_looked_up_by_username(self):
        status, data = self.client.get(f"/api/users/{self.member.username}")
        self.assertEqual(200, status)
        self.assertEqual(self.member.id, data["id"])

    def test_user_list_requires_authentication(self):
        status, _ = self.client.get("/api/users")
        self.assertEqual(403, status)

        self.client.api_key = self.member_key.key
        status, _ = self.client.get("/api/users")
        self.assertEqual(200, status)

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


class FilteringTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()
        self.admin = models.User.objects.filter(is_staff=True).first()
        self.admin_key = models.ApiKey.objects.get_or_create(user=self.admin)[0]

    def test_drinks_filtered_by_username(self):
        drink = models.Drink.objects.exclude(user__isnull=True).first()
        username = drink.user.username
        expected = models.Drink.objects.filter(user__username=username).count()

        status, data = self.client.get(f"/api/drinks?username={username}&page_size=100")
        self.assertEqual(200, status)
        self.assertEqual(expected, len(data["results"]))

        status, data = self.client.get("/api/drinks?username=no-such-user")
        self.assertEqual(200, status)
        self.assertEqual([], data["results"])

    def test_drinks_filtered_by_keg_and_session(self):
        drink = models.Drink.objects.exclude(session__isnull=True).first()

        status, data = self.client.get(f"/api/drinks?keg={drink.keg_id}&page_size=100")
        self.assertEqual(200, status)
        self.assertGreater(len(data["results"]), 0)
        self.assertTrue(all(d["keg"]["id"] == drink.keg_id for d in data["results"]))

        status, data = self.client.get(f"/api/drinks?session={drink.session_id}&page_size=100")
        self.assertEqual(200, status)
        self.assertGreater(len(data["results"]), 0)
        self.assertTrue(all(d["session_id"] == drink.session_id for d in data["results"]))

    def test_kegs_filtered_by_status(self):
        expected = models.Keg.objects.filter(status=models.Keg.STATUS_ON_TAP).count()
        status, data = self.client.get("/api/kegs?status=on_tap&page_size=100")
        self.assertEqual(200, status)
        self.assertEqual(expected, len(data["results"]))

    def test_sessions_filtered_by_date(self):
        session = models.DrinkingSession.objects.first()
        dt = session.start_time
        status, data = self.client.get(
            f"/api/sessions?year={dt.year}&month={dt.month}&page_size=100"
        )
        self.assertEqual(200, status)
        self.assertIn(session.id, [s["id"] for s in data["results"]])

        status, data = self.client.get("/api/sessions?year=1999")
        self.assertEqual(200, status)
        self.assertEqual([], data["results"])

    def test_events_filtered_by_since(self):
        max_id = models.SystemEvent.objects.latest("id").id
        status, data = self.client.get(f"/api/events?since={max_id}")
        self.assertEqual(200, status)
        self.assertEqual([], data["results"])

        status, data = self.client.get(f"/api/events?since={max_id - 2}")
        self.assertEqual(200, status)
        self.assertEqual(2, len(data["results"]))

    def test_users_search(self):
        self.client.api_key = self.admin_key.key
        status, data = self.client.get("/api/users?search=alic&page_size=100")
        self.assertEqual(200, status)
        self.assertEqual(["alice"], [u["username"] for u in data["results"]])

    def test_page_size_is_honored_and_capped(self):
        total = models.Drink.objects.count()
        self.assertGreater(total, 10)

        status, data = self.client.get("/api/drinks?page_size=100")
        self.assertEqual(200, status)
        self.assertEqual(total, len(data["results"]))

        status, data = self.client.get("/api/drinks?page_size=3")
        self.assertEqual(200, status)
        self.assertEqual(3, len(data["results"]))


class CurrentSessionTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()

    def test_no_active_session_returns_404(self):
        # Fixture sessions are long in the past.
        status, _ = self.client.get("/api/sessions/current")
        self.assertEqual(404, status)

    def test_active_session_is_returned(self):
        session = models.DrinkingSession.objects.latest()
        session.start_time = timezone.now() - datetime.timedelta(minutes=10)
        session.end_time = timezone.now() + datetime.timedelta(minutes=10)
        session.save()

        status, data = self.client.get("/api/sessions/current")
        self.assertEqual(200, status)
        self.assertEqual(session.id, data["id"])


class StatsEndpointsTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()

    def test_system_stats(self):
        status, data = self.client.get("/api/stats/system")
        self.assertEqual(200, status)
        self.assertEqual(models.Drink.objects.count(), data["total_pours"])
        # Drinker keys must be usernames, not numeric user ids.
        for name in data["volume_by_drinker"]:
            self.assertFalse(name.isdigit(), name)

    def test_user_stats(self):
        drink = models.Drink.objects.exclude(user__isnull=True).first()
        username = drink.user.username
        expected = models.Drink.objects.filter(user__username=username).count()
        status, data = self.client.get(f"/api/users/{username}/stats")
        self.assertEqual(200, status)
        self.assertEqual(expected, data["total_pours"])

    def test_keg_stats(self):
        keg = models.Keg.objects.first()
        status, data = self.client.get(f"/api/kegs/{keg.id}/stats")
        self.assertEqual(200, status)
        self.assertEqual(models.Drink.objects.filter(keg=keg).count(), data["total_pours"])

    def test_session_stats(self):
        session = models.DrinkingSession.objects.first()
        status, data = self.client.get(f"/api/sessions/{session.id}/stats")
        self.assertEqual(200, status)
        self.assertEqual(models.Drink.objects.filter(session=session).count(), data["total_pours"])

    def test_user_stats_respect_site_privacy(self):
        self.site.privacy = models.KegbotSite.PRIVACY_CHOICE_MEMBERS
        self.site.save()
        username = models.Drink.objects.exclude(user__isnull=True).first().user.username
        status, _ = self.client.get(f"/api/users/{username}/stats")
        self.assertEqual(403, status)


class MeEndpointTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()
        self.user = models.User.objects.get(username="alice")
        self.api_key = models.ApiKey.objects.get_or_create(user=self.user)[0]

    def test_anonymous_caller_gets_null_user_even_on_private_site(self):
        self.site.privacy = models.KegbotSite.PRIVACY_CHOICE_STAFF
        self.site.save()

        status, data = self.client.get("/api/users/me")
        self.assertEqual(200, status)
        self.assertIsNone(data["user"])
        self.assertEqual("staff", data["site"]["privacy"])
        self.assertEqual(self.site.title, data["site"]["title"])
        # The boot payload must not leak pour-derived data.
        self.assertNotIn("stats", data["site"])

    def test_authenticated_caller_gets_user(self):
        self.client.api_key = self.api_key.key
        status, data = self.client.get("/api/users/me")
        self.assertEqual(200, status)
        self.assertEqual("alice", data["user"]["username"])

    def test_metadata_fields_are_present(self):
        status, data = self.client.get("/api/users/me")
        self.assertEqual(200, status)
        self.assertTrue(data["have_sessions"])
        self.assertIn("can_invite", data)
        self.assertEqual(
            ["webhook"],
            [p["short_name"] for p in data["plugins"]],
        )

    def test_sets_csrf_cookie(self):
        response = self.client.client.get("/api/users/me")
        self.assertEqual(200, response.status_code)
        self.assertIn("csrftoken", response.cookies)


class SetupGateTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()

    def test_setup_required_returns_json(self):
        self.site.is_setup = False
        self.site.save()
        status, data = self.client.get("/api/users/me")
        self.assertEqual(403, status)
        self.assertEqual({"error": "setup_required"}, data)

    def test_upgrade_required_returns_json(self):
        self.site.server_version = "0.0.1"
        self.site.save()
        status, data = self.client.get("/api/status")
        self.assertEqual(403, status)
        self.assertEqual("upgrade_required", data["error"])
        self.assertEqual("0.0.1", data["installed_version"])


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
