"""Unittests for pykeg.web.api"""

from django.test import TestCase

from pykeg.core import defaults, models
from pykeg.util import kbjson

# Helper methods


def create_site():
    return defaults.set_defaults(set_is_setup=True, create_controller=True)


class BaseApiTestCase(TestCase):
    def get(self, subpath, data={}, follow=False, **extra):
        response = self.client.get(f"/api/{subpath}", data=data, follow=follow, **extra)
        return response, kbjson.loads(response.content)

    def post(self, subpath, data={}, follow=False, **extra):
        response = self.client.post(f"/api/{subpath}", data=data, follow=follow, **extra)
        return response, kbjson.loads(response.content)


class ApiClientNoSiteTestCase(BaseApiTestCase):
    def testNotSetUp(self):
        """Api endpoints should all error out prior to site setup."""

        endpoints = ("events/", "taps/")
        for endpoint in endpoints:
            response, data = self.get(endpoint)
            self.assertEqual(data.meta.result, "error")
            self.assertEqual(data.error.code, "BadRequestError")

        create_site()

        # Ordinary results expected after site installed.
        for endpoint in endpoints:
            response, data = self.get(endpoint)
            self.assertEqual(data.meta.result, "ok")


class ApiClientTestCase(BaseApiTestCase):
    def setUp(self):
        self.site = create_site()
        self.admin = models.User.objects.create(username="admin", is_staff=True)
        self.admin.set_password("testpass")
        self.admin.save()

        self.normal_user = models.User.objects.create(username="normal_user", is_staff=True)
        self.normal_user.set_password("testpass")
        self.normal_user.save()

        self.apikey = models.ApiKey.objects.create(user=self.admin, key="123")
        self.bad_apikey = models.ApiKey.objects.create(user=self.normal_user, key="456")

        self.tap = models.KegTap.objects.all().first()

    def start_keg(self):
        return models.Keg.start_keg(
            "kegboard.flow0",
            beverage_name="Test Brew",
            beverage_type="beer",
            producer_name="Test Producer",
            style_name="Test Style",
        )

    def test_defaults(self):
        response, data = self.get("events/")
        self.assertEqual(data.objects, [])

        response, data = self.get("taps/")
        taps = data.objects
        self.assertEqual(2, len(taps))
        self.assertEqual("Main Tap", taps[0].name)
        self.assertEqual("kegboard.flow0", taps[0].meter_name)
        self.assertEqual("Second Tap", taps[1].name)
        self.assertEqual("kegboard.flow1", taps[1].meter_name)

        for tap in taps:
            response1, data1 = self.get(f"taps/{tap.meter_name}")
            self.assertEqual(data1.meta.result, "ok")

            response2, data2 = self.get(f"taps/{tap.id}")
            self.assertEqual(data2.meta.result, "ok")

            self.assertEqual(data1, data2)

    def test_api_access(self):
        endpoint = "controllers"

        # No API key.
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, "error")
        self.assertEqual(data.error.code, "NoAuthTokenError")

        # Non-existent key.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY="foobar")
        self.assertEqual(data.meta.result, "error")
        self.assertEqual(data.error.code, "BadApiKeyError")

        # Key exists, staff user.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY=self.bad_apikey.key)
        self.assertEqual(data.meta.result, "ok")

        # Finally ok.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, "ok")

        endpoint = "events/"

        # Alter privacy and compare.
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, "ok")
        self.site.privacy = "members"
        self.site.save()

        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, "error")

        self.client.login(username="admin", password="testpass")
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, "ok")

        # Alter to staff-only.
        self.site.privacy = "staff"
        self.site.save()
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, "ok")

        self.client.logout()
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, "error")
        self.assertEqual(data.error.code, "NoAuthTokenError")

    def test_record_drink(self):
        response, data = self.get(f"taps/{self.tap.id}")
        self.assertEqual(data.meta.result, "ok")
        self.assertEqual(data.object.get("current_keg"), None)

        self.start_keg()

        response, data = self.post(f"taps/{self.tap.id}", data={"ticks": 1000})
        self.assertEqual(data.meta.result, "error")
        self.assertEqual(data.error.code, "NoAuthTokenError")

        response, data = self.post(
            f"taps/{self.tap.id}",
            HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={"ticks": 1000, "username": self.normal_user.username},
        )
        self.assertEqual(data.meta.result, "ok")
        drink = data.object
        self.assertEqual(drink.id, models.Drink.objects.latest("id").id)

        response, data = self.get("status", HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, "ok")
        users = data.object.get("active_users", [])
        self.assertEqual(1, len(users))
        active_user = users[0]
        self.assertEqual(self.normal_user.username, active_user.username)

    def test_record_drink_usernames(self):
        self.start_keg()

        models.User.objects.create(username="test.123")
        response, data = self.post(
            f"taps/{self.tap.id}",
            HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={"ticks": 1000, "username": "test.123"},
        )
        self.assertEqual(data.meta.result, "ok")

    def test_controller_data(self):
        for endpoint in ("controllers", "flow-meters"):
            response, data = self.get(endpoint)
            self.assertEqual(data.meta.result, "error")
            self.assertEqual(data.error.code, "NoAuthTokenError")

        response, data = self.get("controllers", HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, "ok")
        controllers = models.Controller.objects.all()
        expected = {
            "objects": [
                {
                    "id": controllers[0].id,
                    "name": "kegboard",
                }
            ],
            "meta": {
                "result": "ok",
            },
        }
        self.assertEqual(expected, data)

        response, data = self.get("flow-meters", HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, "ok")
        meters = models.FlowMeter.objects.all()
        expected = {
            "objects": [
                {
                    "id": meters[0].id,
                    "ticks_per_ml": 2.724,
                    "port_name": "flow0",
                    "controller": {
                        "id": controllers[0].id,
                        "name": "kegboard",
                    },
                    "name": "kegboard.flow0",
                },
                {
                    "id": meters[1].id,
                    "ticks_per_ml": 2.724,
                    "port_name": "flow1",
                    "controller": {"id": controllers[0].id, "name": "kegboard"},
                    "name": "kegboard.flow1",
                },
            ],
            "meta": {"result": "ok"},
        }
        self.assertEqual(expected, data)

    def test_auth_tokens(self):
        response, data = self.get("auth-tokens/nfc/deadbeef", HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, "error")
        self.assertEqual(response.status_code, 404)

        models.AuthenticationToken.create_auth_token(
            "nfc", "deadbeef", username=self.normal_user.username
        )
        response, data = self.get("auth-tokens/nfc/deadbeef", HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, "ok")
        self.assertEqual(data.object.auth_device, "nfc")
        self.assertEqual(data.object.token_value, "deadbeef")
        self.assertEqual(data.object.username, "normal_user")

    def test_create_tap(self):
        response, data = self.post("taps/", data={"name": "Third Tap"})
        self.assertEqual(data.meta.result, "error")
        self.assertEqual(data.error.code, "NoAuthTokenError")

        response, data = self.post(
            "taps/", data={"name": "Third Tap"}, HTTP_X_KEGBOT_API_KEY=self.apikey.key
        )
        self.assertEqual(data.meta.result, "ok")
        self.assertEqual("Third Tap", data.object.name)
        self.assertEqual(3, models.KegTap.objects.count())


class RetiredEndpointsTestCase(BaseApiTestCase):
    def setUp(self):
        self.site = create_site()

    def test_retired_endpoints_are_gone(self):
        retired = (
            "version",
            "login",
            "logout",
            "get-api-key",
            "devices/link",
            "drinks",
            "drinks/last",
            "kegs/",
            "kegs/1",
            "keg-sizes/",
            "sessions/",
            "sessions/current",
            "sound-events/",
            "stats/",
            "users/",
            "users/someuser",
            "new-user/",
            "pictures/",
            "taps/1/activate",
            "taps/1/calibrate",
            "auth-tokens/nfc/deadbeef/assign",
            "thermo-sensors/foo/logs",
        )
        for endpoint in retired:
            response, data = self.get(endpoint)
            self.assertEqual(410, response.status_code, f"expected 410 for {endpoint}")
            self.assertEqual("error", data.meta.result)
            self.assertEqual("GoneError", data.error.code)

    def test_deprecation_header(self):
        for endpoint in ("taps/", "version"):
            response, data = self.get(endpoint)
            self.assertEqual("true", response.headers.get("Deprecation"))
