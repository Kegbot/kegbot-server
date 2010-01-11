# Copyright 2009 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Builds a test suite for all tests in the 'core' directory.

The django-admin command `tests` looks for a tests.py file and expects a suite()
routine to return a unittest.TestSuite.
"""

import unittest

from pykeg.core import alarm_unittest
from pykeg.core import flow_meter_unittest
from pykeg.core import kegbot_unittest
from pykeg.core import models_unittest
from pykeg.core import units_unittest
from pykeg.core import util_unittest
from pykeg.core.net import kegnet_unittest
from pykeg.hw.kegboard import kegboard_unittest
from pykeg.hw.kegboard import crc16_unittest

ALL_TEST_MODULES = (
    alarm_unittest,
    flow_meter_unittest,
    models_unittest,
    units_unittest,
    util_unittest,
    kegnet_unittest,
    kegbot_unittest,
    kegboard_unittest,
    crc16_unittest,
)

def suite():
  suite = unittest.TestSuite()
  for module in ALL_TEST_MODULES:
    suite.addTests(unittest.TestLoader().loadTestsFromModule(module))
  return suite
