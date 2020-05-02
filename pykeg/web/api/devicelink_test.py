"""Unittests for pykeg.web.api.devicelink"""

from django.core.cache import cache
from django.test import TransactionTestCase
from pykeg.core import models
from pykeg.web.api import devicelink


class DevicelinkTest(TransactionTestCase):
    def test_pairing(self):
        code = devicelink.start_link("test1")
        key = "".join((devicelink.CACHE_PREFIX, code))
        saved = cache.get(key)
        self.assertEqual({"name": "test1", "linked": False}, saved)

        status = devicelink.get_status(code)
        self.assertIsNone(status)

        devicelink.confirm_link(code)
        saved = cache.get(key)
        self.assertEqual({"name": "test1", "linked": True}, saved)

        status = devicelink.get_status(code)
        self.assertIsNotNone(status)
        apikey = models.ApiKey.objects.get(key=status)
        self.assertEqual("test1", apikey.device.name)

        # Entry has been deleted.
        self.assertRaises(devicelink.LinkExpiredException, devicelink.get_status, code)

        self.assertRaises(devicelink.LinkExpiredException, devicelink.get_status, "bogus-code")

    def test_build_code(self):
        code = devicelink._build_code(6)
        self.assertEqual(7, len(code))
        self.assertEqual("-", code[3])

        code = devicelink._build_code(3)
        self.assertEqual(4, len(code))
        self.assertEqual("-", code[1])
