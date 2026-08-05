"""Tests for the kegboard event protocol endpoint."""

import json
from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from pykeg.core import models
from pykeg.core.util import get_version
from pykeg.kegboard import state

ENDPOINT = "/api/kegboard-event"
DEVICE = "kegboard-a1b2c3"

STATUS_DATA = {
    "state": "heartbeat",
    "fw_version": "4.0.0",
    "uptime_ms": 12345,
    "events_dropped": 0,
    "config": {"heartbeat_ms": 60000, "pour_update_ms": 1000, "queue_capacity": 16},
}


class KegboardTestCase(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def setUp(self):
        cache.clear()
        self.site = models.KegbotSite.get()
        self.site.server_version = get_version()
        self.site.save()
        self.controller = models.Controller.objects.get(name="kegboard")
        self.user = models.User.objects.exclude(username="guest").first()

    def pair(self):
        self.controller.auth_token = "kbe_testtoken"
        self.controller.save()
        return self.controller.auth_token

    def post(self, events, device=DEVICE, boot_id="boot-1", token=None):
        headers = {}
        if token:
            headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.client.post(
            ENDPOINT,
            data=json.dumps(
                {
                    "v": 1,
                    "device": device,
                    "boot_id": boot_id,
                    "sent_uptime_ms": 1000,
                    "events": events,
                }
            ),
            content_type="application/json",
            **headers,
        )

    def status_event(self, event_id=1, **overrides):
        return {"id": event_id, "type": "status", "age_ms": 0, "data": {**STATUS_DATA, **overrides}}

    def pour_event(self, event_id=1, **overrides):
        data = {
            "meter_number": 0,
            "pour_id": "pour-1",
            "volume_ml": 355.0,
            "duration_ms": 7100,
            "ticks": 1919,
            **overrides,
        }
        return {"id": event_id, "type": "pour", "age_ms": 5000, "data": data}


class EnvelopeTest(KegboardTestCase):
    def test_malformed_batch(self):
        response = self.client.post(ENDPOINT, data="{nope", content_type="application/json")
        self.assertEqual(400, response.status_code)

        response = self.post([])
        self.assertEqual(400, response.status_code)

    def test_unsupported_version(self):
        response = self.client.post(
            ENDPOINT,
            data=json.dumps(
                {
                    "v": 2,
                    "device": DEVICE,
                    "boot_id": "b",
                    "sent_uptime_ms": 0,
                    "events": [self.status_event()],
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(400, response.status_code)

    def test_rejected_batch_is_pinned_to_the_roster(self):
        # A board whose batches all 400 still surfaces on the dashboard,
        # with the rejection reason, instead of silently "pairing" forever.
        response = self.client.post(
            ENDPOINT,
            data=json.dumps({"v": 1, "device": DEVICE, "events": []}),
            content_type="application/json",
        )
        self.assertEqual(400, response.status_code)
        entry = state.get_device(DEVICE)
        self.assertIn("invalid batch", entry["last_error"])
        self.assertTrue(entry["last_seen"])

        # A good batch clears the error.
        self.post([self.status_event()])
        self.assertIsNone(state.get_device(DEVICE)["last_error"])

    def test_oversized_batch(self):
        big = "x" * (17 * 1024)
        response = self.client.post(
            ENDPOINT, data=json.dumps({"v": 1, "junk": big}), content_type="application/json"
        )
        self.assertEqual(413, response.status_code)


class SetupModeTest(KegboardTestCase):
    def test_setup_mode_returns_503(self):
        # 5xx keeps events queued on the device until the site is ready;
        # the /api setup gate's 403 would make boards drop their batches.
        self.site.is_setup = False
        self.site.save()
        response = self.post([self.status_event()])
        self.assertEqual(503, response.status_code)


class PairingTest(KegboardTestCase):
    def test_unpaired_device_is_pending(self):
        response = self.post([self.status_event()])
        self.assertEqual(401, response.status_code)
        self.assertEqual({"pairing": {"state": "pending"}}, response.json())

        entry = state.get_device(DEVICE)
        self.assertEqual("pending", entry["state"])
        self.assertTrue(entry["first_seen"])
        self.assertTrue(entry["ip"])

        # first_seen is stable across announcements.
        first_seen = entry["first_seen"]
        self.post([self.status_event()])
        self.assertEqual(first_seen, state.get_device(DEVICE)["first_seen"])

    def test_denied_device(self):
        state.set_device_state(DEVICE, state.STATE_DENIED)
        response = self.post([self.status_event()])
        self.assertEqual(401, response.status_code)
        self.assertEqual({"pairing": {"state": "denied"}}, response.json())

    def test_token_delivered_exactly_once(self):
        state.stage_token(DEVICE, "kbe_fresh")
        response = self.post([self.status_event()])
        self.assertEqual(401, response.status_code)
        self.assertEqual({"pairing": {"state": "allowed", "token": "kbe_fresh"}}, response.json())

        # The slot is consumed: the same request now re-enters pairing.
        response = self.post([self.status_event()])
        self.assertEqual({"pairing": {"state": "pending"}}, response.json())

    def test_bad_token_reenters_pairing(self):
        self.pair()
        response = self.post([self.status_event()], token="kbe_wrong")
        self.assertEqual(401, response.status_code)
        self.assertEqual({"pairing": {"state": "pending"}}, response.json())


class DedupTest(KegboardTestCase):
    def test_batch_replay_is_idempotent(self):
        token = self.pair()
        events = [self.pour_event(event_id=7)]
        self.assertEqual(200, self.post(events, token=token).status_code)
        self.assertEqual(1, models.Drink.objects.filter(pour_id="pour-1").count())

        # Same batch again (lost 2xx): nothing new.
        drinks_before = models.Drink.objects.count()
        self.assertEqual(200, self.post(events, token=token).status_code)
        self.assertEqual(drinks_before, models.Drink.objects.count())

    def test_new_boot_resets_cursor(self):
        token = self.pair()
        self.post([self.pour_event(event_id=7)], boot_id="boot-1", token=token)
        # Same event id in a new boot is a new event.
        self.post([self.pour_event(event_id=7, pour_id="pour-2")], boot_id="boot-2", token=token)
        self.assertTrue(models.Drink.objects.filter(pour_id="pour-2").exists())

    def test_pour_id_is_second_line_of_defense(self):
        token = self.pair()
        self.post([self.pour_event(event_id=1)], boot_id="boot-1", token=token)
        # Different transport identity, same pour_id: still one drink.
        self.post([self.pour_event(event_id=1)], boot_id="boot-2", token=token)
        self.assertEqual(1, models.Drink.objects.filter(pour_id="pour-1").count())


class PourTest(KegboardTestCase):
    def test_pour_records_drink(self):
        token = self.pair()
        response = self.post([self.pour_event(tick_series="0:3 100:14")], token=token)
        self.assertEqual(200, response.status_code)

        drink = models.Drink.objects.get(pour_id="pour-1")
        self.assertEqual(355.0, drink.volume_ml)
        self.assertEqual(7, drink.duration)
        # age_ms anchors the pour five seconds in the past.
        age = timezone.now() - drink.time
        self.assertTrue(timedelta(seconds=4) < age < timedelta(seconds=30))

    def test_pour_without_grant_is_guest(self):
        token = self.pair()
        self.post([self.pour_event()], token=token)
        drink = models.Drink.objects.get(pour_id="pour-1")
        self.assertTrue(drink.is_guest_pour())

    def test_pour_with_grant_is_attributed(self):
        # Identity never travels down: the pour carries only our
        # grant_id, and attribution comes from the grant record.
        token = self.pair()
        models.AuthenticationToken.objects.create(
            auth_device="core.rfid", token_value="0089f2c4", user=self.user
        )
        event = {
            "id": 1,
            "type": "token",
            "age_ms": 0,
            "data": {"auth_device": "core.rfid", "token": "0089f2c4", "action": "attached"},
        }
        response = self.post([event], token=token)
        grant_id = response.json()["commands"][0]["data"]["grant_id"]

        self.post([self.pour_event(event_id=2, grant_id=grant_id)], token=token)
        drink = models.Drink.objects.get(pour_id="pour-1")
        self.assertEqual(self.user, drink.user)

    def test_pour_with_unknown_grant_is_guest(self):
        token = self.pair()
        self.post([self.pour_event(grant_id="g_gone")], token=token)
        drink = models.Drink.objects.get(pour_id="pour-1")
        self.assertTrue(drink.is_guest_pour())

    def test_pour_on_unbound_meter_is_dropped(self):
        token = self.pair()
        response = self.post([self.pour_event(meter_number=9)], token=token)
        self.assertEqual(200, response.status_code)
        self.assertFalse(models.Drink.objects.filter(pour_id="pour-1").exists())

    def test_pour_update_is_stashed(self):
        token = self.pair()
        event = {
            "id": 1,
            "type": "pour_update",
            "age_ms": 0,
            "data": {
                "meter_number": 0,
                "pour_id": "pour-1",
                "volume_ml": 120.4,
                "duration_ms": 2400,
            },
        }
        self.assertEqual(200, self.post([event], token=token).status_code)
        meter = models.FlowMeter.objects.get(controller=self.controller, port_name="flow0")
        update = state.get_pour_update(meter.tap_id)
        self.assertEqual(120.4, update["volume_ml"])
        self.assertFalse(models.Drink.objects.filter(pour_id="pour-1").exists())


class TemperatureTest(KegboardTestCase):
    def test_temperature_logged(self):
        token = self.pair()
        event = {
            "id": 1,
            "type": "temperature",
            "age_ms": 0,
            "data": {"sensor": "thermo-28ff", "temp_c": 4.25},
        }
        self.assertEqual(200, self.post([event], token=token).status_code)
        sensor = models.ThermoSensor.objects.get(raw_name="kegboard.thermo-28ff")
        self.assertEqual(4.25, sensor.LastLog().temp)


class TokenAuthTest(KegboardTestCase):
    def token_event(self, value, event_id=1):
        return {
            "id": event_id,
            "type": "token",
            "age_ms": 0,
            "data": {"auth_device": "core.rfid", "token": value, "action": "attached"},
        }

    def test_assigned_token_creates_a_grant(self):
        token = self.pair()
        models.AuthenticationToken.objects.create(
            auth_device="core.rfid", token_value="0089f2c4", user=self.user
        )
        response = self.post([self.token_event("0089f2c4")], token=token)
        commands = response.json()["commands"]
        self.assertEqual(1, len(commands))
        self.assertEqual("authorize", commands[0]["type"])
        grant = commands[0]["data"]
        # All meters; the relays bound to their taps; no identity on the wire.
        self.assertEqual([0, 1], grant["meter_numbers"])
        self.assertEqual([0, 1], grant["relay_numbers"])
        self.assertTrue(grant["grant_id"].startswith("g_"))
        self.assertEqual(30000, grant["max_idle_ms"])
        self.assertNotIn("user", grant)
        # The grant record resolves to the token's user server-side.
        self.assertEqual(self.user.username, state.get_grant(grant["grant_id"])["user"])

    def test_grant_end_is_accepted(self):
        token = self.pair()
        event = {
            "id": 1,
            "type": "grant_end",
            "age_ms": 0,
            "data": {
                "meter_numbers": [0],
                "reason": "max_idle",
                "grant_id": "g_5501",
                "volume_ml": 355.0,
                "duration_ms": 42000,
            },
        }
        self.assertEqual(200, self.post([event], token=token).status_code)

    def test_unknown_token_is_denied(self):
        token = self.pair()
        response = self.post([self.token_event("beefbeef")], token=token)
        commands = response.json()["commands"]
        self.assertEqual("deny", commands[0]["type"])
        self.assertEqual("Unknown token", commands[0]["data"]["reason"])

    def test_unassigned_token_is_denied(self):
        token = self.pair()
        models.AuthenticationToken.objects.create(auth_device="core.rfid", token_value="0089f2c4")
        response = self.post([self.token_event("0089f2c4")], token=token)
        commands = response.json()["commands"]
        self.assertEqual("deny", commands[0]["type"])

    def test_commands_resent_until_acked(self):
        token = self.pair()
        models.AuthenticationToken.objects.create(
            auth_device="core.rfid", token_value="0089f2c4", user=self.user
        )
        response = self.post([self.token_event("0089f2c4")], token=token)
        command = response.json()["commands"][0]

        # Still pending on the next exchange.
        response = self.post([self.status_event(event_id=2)], token=token)
        self.assertEqual([command], response.json()["commands"])

        ack = {
            "id": 3,
            "type": "command_result",
            "age_ms": 0,
            "data": {"command": command["id"], "result": "ok"},
        }
        response = self.post([ack], token=token)
        self.assertEqual([], response.json()["commands"])


class StatusTest(KegboardTestCase):
    def test_status_updates_health_and_meters(self):
        token = self.pair()
        event = self.status_event(
            wifi_rssi_dbm=-61,
            meters=[
                {"meter_number": 0, "total_ticks": 1000, "ml_per_tick": 0.5},
                {"meter_number": 2, "total_ticks": 0, "ml_per_tick": 0.25},
            ],
        )
        self.assertEqual(200, self.post([event], token=token).status_code)

        entry = state.get_device(self.controller.name)
        self.assertEqual("paired", entry["state"])
        self.assertEqual("4.0.0", entry["fw_version"])
        self.assertEqual(-61, entry["wifi_rssi_dbm"])

        meter0 = models.FlowMeter.objects.get(controller=self.controller, port_name="flow0")
        self.assertEqual(2.0, meter0.ticks_per_ml)
        # A new meter number is created on sight.
        meter2 = models.FlowMeter.objects.get(controller=self.controller, port_name="flow2")
        self.assertEqual(4.0, meter2.ticks_per_ml)

    def test_unknown_event_type_is_ignored(self):
        token = self.pair()
        event = {"id": 1, "type": "hologram", "age_ms": 0, "data": {"x": 1}}
        self.assertEqual(200, self.post([event], token=token).status_code)

    def test_bad_payload_is_dropped_not_fatal(self):
        token = self.pair()
        bad = {"id": 1, "type": "pour", "age_ms": 0, "data": {"nope": True}}
        good = self.pour_event(event_id=2)
        self.assertEqual(200, self.post([bad, good], token=token).status_code)
        self.assertTrue(models.Drink.objects.filter(pour_id="pour-1").exists())
