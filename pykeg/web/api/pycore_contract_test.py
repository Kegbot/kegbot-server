"""Contract tests for the legacy API surface kegbot-pycore depends on.

kegbot-pycore's WebBackend (via the old kegbot.api kbapi client) calls
exactly these endpoints and reads the asserted fields. The kegweb
fullscreen page additionally polls the events endpoint. This is the
compatibility contract for the deprecated v1 API: these tests must keep
passing until pycore moves to its replacement protocol.
"""

from django.test import TestCase

from pykeg.core import defaults, models
from pykeg.util import kbjson

METER_NAME = "kegboard.flow0"
API_KEY = "123"


class PycoreContractTestCase(TestCase):
    def setUp(self):
        self.site = defaults.set_defaults(set_is_setup=True, create_controller=True)
        self.admin = models.User.objects.create(username="admin", is_staff=True)
        self.apikey = models.ApiKey.objects.create(user=self.admin, key=API_KEY)

    def get(self, subpath, data={}):
        data = dict(data, api_key=API_KEY)
        response = self.client.get(f"/api/{subpath}", data=data)
        return response, kbjson.loads(response.content)

    def post(self, subpath, data={}):
        data = dict(data, api_key=API_KEY)
        response = self.client.post(f"/api/{subpath}", data=data)
        return response, kbjson.loads(response.content)

    def start_keg(self):
        return models.Keg.start_keg(
            METER_NAME,
            beverage_name="Test Beer",
            beverage_type="beer",
            producer_name="Test Producer",
            style_name="Test Style",
        )

    def test_get_status(self):
        response, data = self.get("status")
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", data.meta.result)

        status = data.object
        self.assertIn("site_info", status)
        self.assertIn("title", status.site_info)
        self.assertIn("server_version", status.site_info)

        # pycore syncs taps from status: meter_name, ml_per_tick, relay_name.
        self.assertEqual(2, len(status.taps))
        for tap in status.taps:
            self.assertIn("meter_name", tap)
            self.assertIn("ml_per_tick", tap)
            self.assertIn("relay_name", tap)

    def test_get_taps(self):
        response, data = self.get("taps")
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", data.meta.result)

        taps = data.objects
        self.assertEqual(2, len(taps))
        self.assertEqual(METER_NAME, taps[0].meter_name)
        tap = models.KegTap.get_from_meter_name(METER_NAME)
        meter = tap.current_meter()
        self.assertAlmostEqual(1 / meter.ticks_per_ml, taps[0].ml_per_tick, places=4)
        toggle = tap.current_toggle()
        expected_relay = toggle.toggle_name() if toggle else ""
        self.assertEqual(expected_relay, taps[0].relay_name)

    def test_record_and_cancel_drink(self):
        self.start_keg()

        response, data = self.post(f"taps/{METER_NAME}", data={"ticks": 2200})
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", data.meta.result)

        drink = data.object
        self.assertIn("id", drink)
        meter = models.KegTap.get_from_meter_name(METER_NAME).current_meter()
        self.assertAlmostEqual(2200 / meter.ticks_per_ml, drink.volume_ml, places=3)
        self.assertIn("session_id", drink)
        self.assertIn("time", drink)

        response, data = self.post("cancel-drink", data={"id": drink.id, "spilled": True})
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", data.meta.result)
        self.assertEqual(0, models.Drink.objects.count())

    def test_record_drink_unknown_meter_is_not_found(self):
        response, data = self.post("taps/unknown.meter", data={"ticks": 100})
        self.assertEqual(404, response.status_code)
        self.assertEqual("error", data.meta.result)
        self.assertEqual("NotFoundError", data.error.code)

    def test_log_sensor_reading(self):
        response, data = self.post("thermo-sensors/kegboard.thermo0", data={"temp_c": 4.5})
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", data.meta.result)

        log = data.object
        self.assertAlmostEqual(4.5, log.temperature_c, places=3)
        self.assertIn("sensor_id", log)
        self.assertIn("time", log)

    def test_get_auth_token(self):
        response, data = self.get("auth-tokens/core.rfid/deadbeef")
        self.assertEqual(404, response.status_code)
        self.assertEqual("error", data.meta.result)
        self.assertEqual("NotFoundError", data.error.code)

        token = models.AuthenticationToken.create_auth_token(
            "core.rfid", "deadbeef", username=self.admin.username
        )
        token.enabled = True
        token.save()

        response, data = self.get("auth-tokens/core.rfid/deadbeef")
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", data.meta.result)

        obj = data.object
        self.assertEqual("core.rfid", obj.auth_device)
        self.assertEqual("deadbeef", obj.token_value)
        self.assertEqual(self.admin.username, obj.username)
        self.assertTrue(obj.enabled)

    def test_create_controller_and_meters(self):
        response, data = self.post(
            "controllers",
            data={"name": "kegboard2", "model_name": "unknown", "serial_number": "unknown"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", data.meta.result)

        controller = data.object
        self.assertIn("id", controller)
        self.assertEqual("kegboard2", controller.name)

        response, data = self.post(
            "flow-meters",
            data={"controller": controller.id, "port_name": "flow0", "ticks_per_ml": 2.2},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", data.meta.result)

        meter = data.object
        self.assertIn("id", meter)
        self.assertEqual("kegboard2.flow0", meter.name)

    def test_get_events(self):
        # The kegweb fullscreen page polls events and reads objects[0].id.
        self.start_keg()

        response, data = self.get("events/")
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", data.meta.result)
        self.assertTrue(len(data.objects) > 0)
        self.assertIn("id", data.objects[0])
        # Newest first.
        ids = [e.id for e in data.objects]
        self.assertEqual(sorted(ids, reverse=True), ids)
