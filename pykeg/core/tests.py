"""Builds a test suite for all tests in the 'core' directory.

The django-admin command `tests` looks for a tests.py file and expects a suite()
routine to return a unittest.TestSuite.
"""
import unittest

import KegbotJsonServer_unittest
import kegbot_unittest
import models_unittest
import StateMachine_unittest
import units_unittest
import util_unittest

from pykeg.core.Devices import Net_unittest

ALL_TEST_MODULES = (
    models_unittest,
    StateMachine_unittest,
    units_unittest,
    util_unittest,
    Net_unittest,
    KegbotJsonServer_unittest,
    kegbot_unittest,
)

def suite():
  suite = unittest.TestSuite()
  for module in ALL_TEST_MODULES:
    suite.addTests(unittest.TestLoader().loadTestsFromModule(module))
  return suite
