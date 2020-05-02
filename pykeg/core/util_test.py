"""Test for util module."""

from builtins import str
from distutils.version import StrictVersion

from pykeg.core import util

from django.test import TestCase


class CoreTests(TestCase):
    def test_get_version(self):
        self.assertNotEqual("0.0.0", util.get_version())
        try:
            util.get_version_object()
        except ValueError as e:
            self.fail("Illegal version: " + str(e))
        self.assertTrue(util.get_version_object().version >= (0, 9, 23))

    def test_must_upgrade(self):
        v100 = StrictVersion("1.0.0")
        v101 = StrictVersion("1.0.1")
        v110 = StrictVersion("1.1.0")

        self.assertTrue(util.should_upgrade(v100, v101))
        self.assertFalse(util.should_upgrade(v100, v100))
        self.assertFalse(util.must_upgrade(v100, v101))
        self.assertTrue(util.must_upgrade(v100, v110))
