import base64
import datetime
import re

from django.contrib.auth.tokens import default_token_generator
from django.core import mail as django_mail
from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
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

    def test_users_are_not_editable_by_members(self):
        self.client.api_key = self.member_key.key
        self.client.add_auth()
        response = self.client.client.patch(
            f"/api/users/{self.member.username}", {"display_name": "hax"}, format="json"
        )
        self.assertEqual(403, response.status_code)

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


class KegTapOperationsTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()
        self.admin = models.User.objects.get(username="admin")
        self.admin.is_staff = True
        self.admin.save()
        self.admin_key = models.ApiKey.objects.get_or_create(user=self.admin)[0]
        self.member = models.User.objects.get(username="alice")
        self.member_key = models.ApiKey.objects.get_or_create(user=self.member)[0]
        self.tap = models.KegTap.objects.get(name="Main Tap")

    def post(self, path, data=None, key=None):
        self.client.api_key = key or self.admin_key.key
        self.client.add_auth()
        return self.client.client.post(path, data or {}, format="json")

    def test_tap_operations_require_admin(self):
        for path in (
            f"/api/taps/{self.tap.id}/end-keg",
            f"/api/taps/{self.tap.id}/attach-keg",
            "/api/taps",
        ):
            response = self.post(path, key=self.member_key.key)
            self.assertEqual(403, response.status_code, path)

    def test_end_and_attach_keg(self):
        keg = self.tap.current_keg
        response = self.post(f"/api/taps/{self.tap.id}/end-keg")
        self.assertEqual(200, response.status_code)
        self.assertIsNone(response.json()["current_keg"])
        keg.refresh_from_db()
        self.assertEqual(models.Keg.STATUS_FINISHED, keg.status)

        response = self.post(f"/api/taps/{self.tap.id}/end-keg")
        self.assertEqual(400, response.status_code)

        response = self.post(f"/api/taps/{self.tap.id}/attach-keg", {"keg_id": keg.id})
        self.assertEqual(200, response.status_code)
        self.assertEqual(keg.id, response.json()["current_keg"]["id"])
        keg.refresh_from_db()
        self.assertEqual(models.Keg.STATUS_ON_TAP, keg.status)

    def test_attach_fails_when_tap_active(self):
        other_keg = models.Keg.objects.exclude(id=self.tap.current_keg_id).first()
        response = self.post(f"/api/taps/{self.tap.id}/attach-keg", {"keg_id": other_keg.id})
        self.assertEqual(400, response.status_code)

    def test_start_keg_creates_and_attaches(self):
        self.post(f"/api/taps/{self.tap.id}/end-keg")
        response = self.post(
            f"/api/taps/{self.tap.id}/start-keg",
            {
                "beverage_name": "Test Brew",
                "producer_name": "Test Brewery",
                "style_name": "IPA",
                "keg_type": "half-barrel",
            },
        )
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertEqual("Test Brew", data["current_keg"]["beverage"]["name"])
        self.assertEqual("on_tap", data["current_keg"]["status"])

    def test_start_keg_requires_beverage(self):
        self.post(f"/api/taps/{self.tap.id}/end-keg")
        response = self.post(f"/api/taps/{self.tap.id}/start-keg", {})
        self.assertEqual(400, response.status_code)

    def test_record_drink_and_spill(self):
        keg = self.tap.current_keg
        served_before = keg.served_volume_ml

        response = self.post(
            f"/api/taps/{self.tap.id}/record-drink",
            {"volume_ml": 400.0, "username": "alice", "shout": "cheers!"},
        )
        self.assertEqual(201, response.status_code)
        data = response.json()
        self.assertEqual("alice", data["user"]["username"])
        self.assertEqual("cheers!", data["shout"])
        keg.refresh_from_db()
        self.assertEqual(served_before + 400.0, keg.served_volume_ml)

        spilled_before = keg.spilled_ml
        response = self.post(
            f"/api/taps/{self.tap.id}/record-drink",
            {"volume_ml": 100.0, "spilled": True},
        )
        self.assertEqual(204, response.status_code)
        keg.refresh_from_db()
        self.assertEqual(spilled_before + 100.0, keg.spilled_ml)

    def test_record_drink_unknown_user(self):
        response = self.post(
            f"/api/taps/{self.tap.id}/record-drink",
            {"volume_ml": 100.0, "username": "nobody"},
        )
        self.assertEqual(400, response.status_code)

    def test_connect_meter(self):
        other_meter = models.FlowMeter.objects.exclude(tap=self.tap).first()
        response = self.post(f"/api/taps/{self.tap.id}/connect-meter", {"meter_id": other_meter.id})
        self.assertEqual(200, response.status_code)
        other_meter.refresh_from_db()
        self.assertEqual(self.tap, other_meter.tap)

        response = self.post(f"/api/taps/{self.tap.id}/connect-meter", {"meter_id": None})
        self.assertEqual(200, response.status_code)
        other_meter.refresh_from_db()
        self.assertIsNone(other_meter.tap)

    def test_tap_crud(self):
        response = self.post("/api/taps", {"name": "Third Tap"})
        self.assertEqual(201, response.status_code)
        tap_id = response.json()["id"]

        self.client.add_auth()
        response = self.client.client.patch(
            f"/api/taps/{tap_id}", {"name": "Renamed Tap"}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Renamed Tap", response.json()["name"])

        response = self.client.client.delete(f"/api/taps/{tap_id}")
        self.assertEqual(204, response.status_code)
        self.assertFalse(models.KegTap.objects.filter(id=tap_id).exists())


class KegOperationsTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()
        self.admin = models.User.objects.get(username="admin")
        self.admin.is_staff = True
        self.admin.save()
        self.admin_key = models.ApiKey.objects.get_or_create(user=self.admin)[0]

    def post(self, path, data=None):
        self.client.api_key = self.admin_key.key
        self.client.add_auth()
        return self.client.client.post(path, data or {}, format="json")

    def test_create_keg_with_existing_beverage(self):
        beverage = models.Beverage.objects.first()
        response = self.post(
            "/api/kegs",
            {"beverage_id": beverage.id, "keg_type": "corny", "description": "spare"},
        )
        self.assertEqual(201, response.status_code)
        data = response.json()
        self.assertEqual("available", data["status"])
        self.assertEqual(beverage.name, data["beverage"]["name"])
        self.assertEqual("spare", data["description"])

    def test_create_keg_with_new_beverage(self):
        response = self.post(
            "/api/kegs",
            {
                "beverage_name": "New Beer",
                "producer_name": "New Brewery",
                "style_name": "Stout",
            },
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual("New Beer", response.json()["beverage"]["name"])

    def test_end_and_reactivate(self):
        keg = models.Keg.objects.create(
            type=models.Beverage.objects.first(), status=models.Keg.STATUS_AVAILABLE
        )
        response = self.post(f"/api/kegs/{keg.id}/end")
        self.assertEqual(200, response.status_code)
        self.assertEqual("finished", response.json()["status"])

        response = self.post(f"/api/kegs/{keg.id}/reactivate")
        self.assertEqual(200, response.status_code)
        self.assertEqual("available", response.json()["status"])

        # Reactivate requires a finished keg.
        response = self.post(f"/api/kegs/{keg.id}/reactivate")
        self.assertEqual(400, response.status_code)

    def test_end_fails_while_on_tap(self):
        keg = models.KegTap.objects.get(name="Main Tap").current_keg
        response = self.post(f"/api/kegs/{keg.id}/end")
        self.assertEqual(400, response.status_code)

    def test_spill(self):
        keg = models.Keg.objects.first()
        before = keg.spilled_ml
        response = self.post(f"/api/kegs/{keg.id}/spill", {"volume_ml": 250.0})
        self.assertEqual(200, response.status_code)
        keg.refresh_from_db()
        self.assertEqual(before + 250.0, keg.spilled_ml)

    def test_edit_keg_notes_but_not_status(self):
        keg = models.Keg.objects.first()
        self.client.api_key = self.admin_key.key
        self.client.add_auth()
        response = self.client.client.patch(
            f"/api/kegs/{keg.id}",
            {"notes": "updated", "status": "finished"},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        keg.refresh_from_db()
        self.assertEqual("updated", keg.notes)
        # Status is read-only on direct edits.
        self.assertEqual(models.Keg.STATUS_ON_TAP, keg.status)

    def test_delete_keg_destroys_drinks(self):
        keg = models.KegTap.objects.get(name="Main Tap").current_keg
        self.assertTrue(keg.drinks.exists())
        self.client.api_key = self.admin_key.key
        self.client.add_auth()
        response = self.client.client.delete(f"/api/kegs/{keg.id}")
        self.assertEqual(204, response.status_code)
        self.assertFalse(models.Keg.objects.filter(id=keg.id).exists())
        self.assertFalse(models.Drink.objects.filter(keg_id=keg.id).exists())


TINY_GIF = base64.b64decode("R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==")


class DrinkManagementTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()
        self.admin = models.User.objects.get(username="admin")
        self.admin.is_staff = True
        self.admin.save()
        self.admin_key = models.ApiKey.objects.get_or_create(user=self.admin)[0]
        self.alice = models.User.objects.get(username="alice")
        self.alice_key = models.ApiKey.objects.get_or_create(user=self.alice)[0]
        self.bob = models.User.objects.get(username="bob")
        self.bob_key = models.ApiKey.objects.get_or_create(user=self.bob)[0]
        self.alice_drink = models.Drink.objects.filter(user=self.alice).first()

    def as_user(self, key):
        self.client.api_key = key
        self.client.add_auth()
        return self.client.client

    def test_owner_may_edit_shout(self):
        response = self.as_user(self.alice_key.key).patch(
            f"/api/drinks/{self.alice_drink.id}", {"shout": "tasty"}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.alice_drink.refresh_from_db()
        self.assertEqual("tasty", self.alice_drink.shout)

    def test_non_owner_may_not_edit_shout(self):
        response = self.as_user(self.bob_key.key).patch(
            f"/api/drinks/{self.alice_drink.id}", {"shout": "graffiti"}, format="json"
        )
        self.assertEqual(403, response.status_code)

    def test_volume_adjustment_is_admin_only(self):
        response = self.as_user(self.alice_key.key).patch(
            f"/api/drinks/{self.alice_drink.id}", {"volume_ml": 9999.0}, format="json"
        )
        self.assertEqual(403, response.status_code)

        keg = self.alice_drink.keg
        served_before = keg.served_volume_ml
        old_volume = self.alice_drink.volume_ml
        response = self.as_user(self.admin_key.key).patch(
            f"/api/drinks/{self.alice_drink.id}", {"volume_ml": old_volume + 10}, format="json"
        )
        self.assertEqual(200, response.status_code)
        keg.refresh_from_db()
        self.assertEqual(served_before + 10, keg.served_volume_ml)

    def test_reassign(self):
        response = self.as_user(self.alice_key.key).post(
            f"/api/drinks/{self.alice_drink.id}/reassign", {"username": "bob"}, format="json"
        )
        self.assertEqual(403, response.status_code)

        response = self.as_user(self.admin_key.key).post(
            f"/api/drinks/{self.alice_drink.id}/reassign", {"username": "bob"}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("bob", response.json()["user"]["username"])

    def test_destroy_is_admin_only_and_supports_spill(self):
        response = self.as_user(self.alice_key.key).delete(f"/api/drinks/{self.alice_drink.id}")
        self.assertEqual(403, response.status_code)

        keg = self.alice_drink.keg
        spilled_before = keg.spilled_ml
        volume = self.alice_drink.volume_ml
        response = self.as_user(self.admin_key.key).delete(
            f"/api/drinks/{self.alice_drink.id}?spilled=true"
        )
        self.assertEqual(204, response.status_code)
        self.assertFalse(models.Drink.objects.filter(id=self.alice_drink.id).exists())
        keg.refresh_from_db()
        self.assertEqual(spilled_before + volume, keg.spilled_ml)

    def test_picture_upload_and_delete(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = SimpleUploadedFile("pour.gif", TINY_GIF, content_type="image/gif")
        response = self.as_user(self.alice_key.key).post(
            f"/api/drinks/{self.alice_drink.id}/picture", {"image": image}, format="multipart"
        )
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.json()["picture"])
        self.alice_drink.refresh_from_db()
        self.assertIsNotNone(self.alice_drink.picture)

        response = self.as_user(self.bob_key.key).delete(
            f"/api/drinks/{self.alice_drink.id}/picture"
        )
        self.assertEqual(403, response.status_code)

        response = self.as_user(self.alice_key.key).delete(
            f"/api/drinks/{self.alice_drink.id}/picture"
        )
        self.assertEqual(204, response.status_code)
        self.alice_drink.refresh_from_db()
        self.assertIsNone(self.alice_drink.picture)

    def test_beverage_picture_upload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        beverage = models.Beverage.objects.first()
        image = SimpleUploadedFile("label.gif", TINY_GIF, content_type="image/gif")
        response = self.as_user(self.alice_key.key).post(
            f"/api/beverages/{beverage.id}/picture", {"image": image}, format="multipart"
        )
        self.assertEqual(403, response.status_code)

        image = SimpleUploadedFile("label.gif", TINY_GIF, content_type="image/gif")
        response = self.as_user(self.admin_key.key).post(
            f"/api/beverages/{beverage.id}/picture", {"image": image}, format="multipart"
        )
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.json()["picture"])


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


@override_settings(EMAIL_BACKEND="pykeg.core.mail.KegbotEmailBackend")
class AccountFlowsTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        cache.clear()  # Reset auth-endpoint throttle state between tests.
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.email_config = "memory://?_default_from_email=test@example.com"
        self.site.save()
        self.alice = models.User.objects.get(username="alice")
        self.alice.set_password("oldpassword")
        self.alice.email = "alice@example.com"
        self.alice.save()
        self.alice_key = models.ApiKey.objects.get_or_create(user=self.alice)[0]

    def as_alice(self):
        self.client.api_key = self.alice_key.key
        self.client.add_auth()
        return self.client.client

    def as_anon(self):
        self.client.api_key = None
        self.client.add_auth()
        return self.client.client

    def test_update_profile(self):
        response = self.as_alice().patch(
            "/api/users/me", {"display_name": "Alice A."}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Alice A.", response.json()["user"]["display_name"])
        self.alice.refresh_from_db()
        self.assertEqual("Alice A.", self.alice.display_name)

    def test_update_profile_requires_auth(self):
        response = self.as_anon().patch("/api/users/me", {"display_name": "Nope"}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_change_password(self):
        response = self.as_alice().post(
            "/api/account/password",
            {"current_password": "wrong", "new_password": "newpassword"},
            format="json",
        )
        self.assertEqual(400, response.status_code)

        response = self.as_alice().post(
            "/api/account/password",
            {"current_password": "oldpassword", "new_password": "newpassword"},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        self.alice.refresh_from_db()
        self.assertTrue(self.alice.check_password("newpassword"))

    def test_change_email_and_confirm(self):
        response = self.as_alice().post(
            "/api/account/email", {"email": "alice-new@example.com"}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(django_mail.outbox))
        body = django_mail.outbox[0].body
        match = re.search(r"/account/confirm-email/(\S+)", body)
        self.assertIsNotNone(match, body)
        token = match.group(1).rstrip("/")

        response = self.as_alice().post(
            "/api/account/confirm-email", {"token": token}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.alice.refresh_from_db()
        self.assertEqual("alice-new@example.com", self.alice.email)

    def test_mugshot_upload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = SimpleUploadedFile("me.gif", TINY_GIF, content_type="image/gif")
        response = self.as_alice().post(
            "/api/account/mugshot", {"image": image}, format="multipart"
        )
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.json()["picture"])
        self.alice.refresh_from_db()
        self.assertIsNotNone(self.alice.mugshot)

    def test_regenerate_api_key(self):
        old_key = self.alice_key.key
        response = self.as_alice().post("/api/account/regenerate-api-key")
        self.assertEqual(200, response.status_code)
        self.assertNotEqual(old_key, response.json()["key"])

    def test_register_public(self):
        response = self.as_anon().post(
            "/api/auth/register",
            {"username": "newuser", "email": "new@example.com", "password": "s3cret"},
            format="json",
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual("newuser", response.json()["username"])
        user = models.User.objects.get(username="newuser")
        self.assertTrue(user.check_password("s3cret"))

    def test_register_duplicate_username(self):
        response = self.as_anon().post(
            "/api/auth/register",
            {"username": "alice", "email": "x@example.com", "password": "pw"},
            format="json",
        )
        self.assertEqual(400, response.status_code)

    def test_register_invite_only(self):
        self.site.registration_mode = "staff-invite-only"
        self.site.save()

        response = self.as_anon().post(
            "/api/auth/register",
            {"username": "invitee", "email": "i@example.com", "password": "pw"},
            format="json",
        )
        self.assertEqual(403, response.status_code)

        invite = models.Invitation.objects.create(for_email="i@example.com", invited_by=self.alice)
        response = self.as_anon().post(
            "/api/auth/register",
            {
                "username": "invitee",
                "email": "i@example.com",
                "password": "pw",
                "invite_code": invite.invite_code,
            },
            format="json",
        )
        self.assertEqual(201, response.status_code)
        self.assertFalse(models.Invitation.objects.filter(id=invite.id).exists())

    def test_register_bad_invite_code(self):
        self.site.registration_mode = "staff-invite-only"
        self.site.save()
        response = self.as_anon().post(
            "/api/auth/register",
            {
                "username": "invitee",
                "email": "i@example.com",
                "password": "pw",
                "invite_code": "bogus",
            },
            format="json",
        )
        self.assertEqual(403, response.status_code)

    def test_password_reset_sends_mail(self):
        response = self.as_anon().post(
            "/api/auth/password-reset", {"email": "alice@example.com"}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(django_mail.outbox))

        django_mail.outbox.clear()
        response = self.as_anon().post(
            "/api/auth/password-reset", {"email": "nobody@example.com"}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(django_mail.outbox))

    def test_password_reset_confirm(self):
        uid = urlsafe_base64_encode(force_bytes(self.alice.pk))
        token = default_token_generator.make_token(self.alice)

        response = self.as_anon().post(
            "/api/auth/password-reset-confirm",
            {"uid": uid, "token": "bad-token", "new_password": "resetpw"},
            format="json",
        )
        self.assertEqual(400, response.status_code)

        response = self.as_anon().post(
            "/api/auth/password-reset-confirm",
            {"uid": uid, "token": token, "new_password": "resetpw"},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        self.alice.refresh_from_db()
        self.assertTrue(self.alice.check_password("resetpw"))

    def test_activate_account(self):
        user = models.User.objects.create(username="pending", email="p@example.com")
        user.set_unusable_password()
        user.activation_key = "activation123"
        user.save()

        response = self.as_anon().post(
            "/api/account/activate",
            {"activation_key": "activation123", "password": "mypw"},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("pending", response.json()["username"])
        user.refresh_from_db()
        self.assertIsNone(user.activation_key)
        self.assertTrue(user.check_password("mypw"))

        # Key is single-use.
        response = self.as_anon().post(
            "/api/account/activate",
            {"activation_key": "activation123", "password": "mypw"},
            format="json",
        )
        self.assertEqual(404, response.status_code)

    def test_invitation_create_and_destroy(self):
        response = self.as_alice().post(
            "/api/invitations", {"for_email": "friend@example.com"}, format="json"
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(1, len(django_mail.outbox))
        invite_id = response.json()["id"]

        response = self.as_alice().delete(f"/api/invitations/{invite_id}")
        self.assertEqual(204, response.status_code)

    def test_invitation_denied_when_not_allowed(self):
        self.site.registration_mode = "staff-invite-only"
        self.site.save()
        response = self.as_alice().post(
            "/api/invitations", {"for_email": "friend@example.com"}, format="json"
        )
        self.assertEqual(403, response.status_code)


class AdminUsersAndSiteTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()
        self.admin = models.User.objects.get(username="admin")
        self.admin.is_staff = True
        self.admin.save()
        self.admin_key = models.ApiKey.objects.get_or_create(user=self.admin)[0]
        self.alice = models.User.objects.get(username="alice")
        self.alice_key = models.ApiKey.objects.get_or_create(user=self.alice)[0]

    def as_admin(self):
        self.client.api_key = self.admin_key.key
        self.client.add_auth()
        return self.client.client

    def as_member(self):
        self.client.api_key = self.alice_key.key
        self.client.add_auth()
        return self.client.client

    def test_admin_creates_user(self):
        response = self.as_member().post(
            "/api/users", {"username": "nope", "password": "pw"}, format="json"
        )
        self.assertEqual(403, response.status_code)

        response = self.as_admin().post(
            "/api/users",
            {"username": "staffer", "password": "pw", "is_staff": True},
            format="json",
        )
        self.assertEqual(201, response.status_code)
        user = models.User.objects.get(username="staffer")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password("pw"))

    def test_admin_edits_user(self):
        response = self.as_admin().patch(
            "/api/users/alice", {"is_active": False, "is_staff": True}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.alice.refresh_from_db()
        self.assertFalse(self.alice.is_active)
        self.assertTrue(self.alice.is_staff)

    def test_guest_cannot_be_disabled(self):
        response = self.as_admin().patch("/api/users/guest", {"is_active": False}, format="json")
        self.assertEqual(400, response.status_code)

    def test_admin_sets_password(self):
        response = self.as_admin().post(
            "/api/users/alice/set-password", {"password": "newpw"}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.alice.refresh_from_db()
        self.assertTrue(self.alice.check_password("newpw"))

    def test_site_settings_read_and_update(self):
        response = self.as_member().get("/api/site")
        self.assertEqual(403, response.status_code)

        response = self.as_admin().get("/api/site")
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.site.title, response.json()["title"])

        response = self.as_admin().patch(
            "/api/site",
            {"title": "Renamed Bar", "privacy": "members", "session_timeout_minutes": 30},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        self.site.refresh_from_db()
        self.assertEqual("Renamed Bar", self.site.title)
        self.assertEqual("members", self.site.privacy)
        self.assertEqual(30, self.site.session_timeout_minutes)

    def test_site_settings_rejects_bad_email_config(self):
        response = self.as_admin().patch("/api/site", {"email_config": "bogus:"}, format="json")
        self.assertEqual(400, response.status_code)

    def test_site_background_image(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = SimpleUploadedFile("bg.gif", TINY_GIF, content_type="image/gif")
        response = self.as_admin().post(
            "/api/site/background-image", {"image": image}, format="multipart"
        )
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.json()["background_image"])
        self.site.refresh_from_db()
        self.assertIsNotNone(self.site.background_image)

    def test_token_user_assignment(self):
        response = self.as_admin().post(
            "/api/auth-tokens",
            {"auth_device": "core.rfid", "token_value": "deadbeef", "user": self.alice.id},
            format="json",
        )
        self.assertEqual(201, response.status_code)
        token = models.AuthenticationToken.objects.get(
            auth_device="core.rfid", token_value="deadbeef"
        )
        self.assertEqual(self.alice, token.user)

        response = self.as_admin().patch(
            f"/api/auth-tokens/{token.id}", {"user": None}, format="json"
        )
        self.assertEqual(200, response.status_code)
        token.refresh_from_db()
        self.assertIsNone(token.user)


@override_settings(EMAIL_BACKEND="pykeg.core.mail.KegbotEmailBackend")
class AdminOpsTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.client = ApiClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.email_config = "memory://?_default_from_email=test@example.com"
        self.site.save()
        self.admin = models.User.objects.get(username="admin")
        self.admin.is_staff = True
        self.admin.save()
        self.admin_key = models.ApiKey.objects.get_or_create(user=self.admin)[0]
        self.alice = models.User.objects.get(username="alice")
        self.alice_key = models.ApiKey.objects.get_or_create(user=self.alice)[0]

    def as_admin(self):
        self.client.api_key = self.admin_key.key
        self.client.add_auth()
        return self.client.client

    def test_ops_require_admin(self):
        self.client.api_key = self.alice_key.key
        for path in ("/api/admin/dashboard", "/api/admin/backups", "/api/admin/logs"):
            status_code, _ = self.client.get(path)
            self.assertEqual(403, status_code, path)

    def test_dashboard(self):
        response = self.as_admin().get("/api/admin/dashboard")
        self.assertEqual(200, response.status_code)
        data = response.json()
        expected_users = (
            models.User.objects.filter(is_active=True).exclude(username="guest").count()
        )
        self.assertEqual(expected_users, data["num_users"])
        self.assertIn("email_configured", data)
        self.assertIn("redis_error", data)

    def test_backups_list_empty(self):
        response = self.as_admin().get("/api/admin/backups")
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.json())

    def test_backup_build_is_enqueued(self):
        from unittest import mock

        with mock.patch("pykeg.core.tasks.build_backup.delay") as delay:
            response = self.as_admin().post("/api/admin/backups")
        self.assertEqual(202, response.status_code)
        delay.assert_called_once()

    def test_delete_unknown_backup(self):
        response = self.as_admin().delete("/api/admin/backups/nope.zip")
        self.assertEqual(404, response.status_code)

    def test_logs(self):
        response = self.as_admin().get("/api/admin/logs")
        self.assertEqual(200, response.status_code)
        self.assertIn("logs", response.json())

    def test_email_test(self):
        response = self.as_admin().post(
            "/api/admin/email-test", {"address": "check@example.com"}, format="json"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(django_mail.outbox))
        self.assertEqual(["check@example.com"], django_mail.outbox[0].to)

    def test_plugin_list(self):
        self.client.api_key = self.alice_key.key
        status_code, _ = self.client.get("/api/admin/plugins")
        self.assertEqual(403, status_code)

        response = self.as_admin().get("/api/admin/plugins")
        self.assertEqual(200, response.status_code)
        plugins = response.json()
        self.assertEqual(["webhook"], [p["short_name"] for p in plugins])
        self.assertTrue(plugins[0]["has_settings"])

    def test_plugin_settings_roundtrip(self):
        response = self.as_admin().get("/api/admin/plugins/webhook/settings")
        self.assertEqual(200, response.status_code)

        response = self.as_admin().put(
            "/api/admin/plugins/webhook/settings",
            {"webhook_urls": "http://example.com/hook"},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("http://example.com/hook", response.json()["webhook_urls"])

        response = self.as_admin().get("/api/admin/plugins/webhook/settings")
        self.assertEqual("http://example.com/hook", response.json()["webhook_urls"])

    def test_unknown_plugin_settings(self):
        response = self.as_admin().get("/api/admin/plugins/nope/settings")
        self.assertEqual(404, response.status_code)


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


class SetupApiTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        self.api = APIClient()
        self.site = models.KegbotSite.objects.all().first()
        self.site.server_version = get_version()
        self.site.save()

    def test_endpoints_closed_when_site_is_setup(self):
        response = self.api.get("/api/setup/status")
        self.assertEqual(403, response.status_code)
        response = self.api.post("/api/setup/finish")
        self.assertEqual(403, response.status_code)

    def test_setup_flow(self):
        self.site.is_setup = False
        self.site.save()

        response = self.api.get("/api/setup/status")
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertTrue(data["need_setup"])
        self.assertEqual(get_version(), data["current_version"])

        response = self.api.post("/api/setup/migrate")
        self.assertEqual(200, response.status_code)

        response = self.api.post(
            "/api/setup/settings",
            {
                "title": "Fresh Bar",
                "privacy": "members",
                "timezone": "America/Los_Angeles",
                "volume_display_units": "metric",
                "enable_sensing": True,
                "enable_users": False,
            },
            format="json",
        )
        self.assertEqual(200, response.status_code)
        self.site.refresh_from_db()
        self.assertEqual("Fresh Bar", self.site.title)
        self.assertEqual("members", self.site.privacy)
        self.assertFalse(self.site.enable_users)

        response = self.api.post(
            "/api/setup/admin-user",
            {"username": "root", "email": "root@example.com", "password": "adminpw"},
            format="json",
        )
        self.assertEqual(201, response.status_code)
        user = models.User.objects.get(username="root")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("adminpw"))

        response = self.api.post("/api/setup/finish")
        self.assertEqual(200, response.status_code)
        self.site.refresh_from_db()
        self.assertTrue(self.site.is_setup)

        # The wizard is closed once setup completes.
        response = self.api.get("/api/setup/status")
        self.assertEqual(403, response.status_code)

    def test_upgrade_flow(self):
        self.site.server_version = "0.0.1"
        self.site.save()

        response = self.api.get("/api/setup/status")
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertTrue(data["need_upgrade"])
        self.assertEqual("0.0.1", data["installed_version"])

        response = self.api.post("/api/setup/upgrade")
        self.assertEqual(200, response.status_code)
        self.site.refresh_from_db()
        self.assertEqual(get_version(), self.site.server_version)

        response = self.api.post("/api/setup/upgrade")
        self.assertEqual(403, response.status_code)

    def test_settings_conflict_when_only_upgrade_needed(self):
        self.site.server_version = "0.0.1"
        self.site.save()
        response = self.api.post("/api/setup/settings", {"title": "X"}, format="json")
        self.assertEqual(409, response.status_code)


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
