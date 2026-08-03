import json

from django.test import TestCase

from pykeg.util.genconstants import genconstants


class GenConstantsTestCase(TestCase):
    def test_output_is_json_serializable(self):
        data = genconstants()
        round_tripped = json.loads(json.dumps(data))
        self.assertEqual(data, round_tripped)

    def test_expected_keys_present(self):
        data = genconstants()
        self.assertEqual("on_tap", data["KEG_STATUS_ON_TAP"])
        self.assertIn("half-barrel", data["KEG_TYPES"])
        self.assertIn("half-barrel", data["KEG_VOLUMES_ML"])
        self.assertEqual(
            ["public", "members", "staff"],
            list(data["PRIVACY_CHOICES"]),
        )
        self.assertIn("UTC", data["TIMEZONES"])
        self.assertIn("drink_poured", data["EVENT_KINDS"])
