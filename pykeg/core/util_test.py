# Copyright 2014 Bevbot LLC, All Rights Reserved
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

"""Test for util module."""

from distutils.version import StrictVersion

from pykeg.core import util

from django.test import TestCase


class CoreTests(TestCase):

    def test_get_version(self):
        self.assertNotEqual('0.0.0', util.get_version())
        try:
            util.get_version_object()
        except ValueError as e:
            self.fail('Illegal version: ' + str(e))
        self.assertTrue(util.get_version_object().version >= (0, 9, 23))

    def test_must_upgrade(self):
        v100 = StrictVersion('1.0.0')
        v101 = StrictVersion('1.0.1')
        v110 = StrictVersion('1.1.0')

        self.assertTrue(util.should_upgrade(v100, v101))
        self.assertFalse(util.should_upgrade(v100, v100))
        self.assertFalse(util.must_upgrade(v100, v101))
        self.assertTrue(util.must_upgrade(v100, v110))
