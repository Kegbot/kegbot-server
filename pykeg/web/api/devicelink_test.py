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

"""Unittests for pykeg.web.api.devicelink"""

from django.core.cache import cache
from django.test import TransactionTestCase
from pykeg.core import models
from pykeg.web.api import devicelink


class DevicelinkTest(TransactionTestCase):
    def test_pairing(self):
        code = devicelink.start_link('test1')
        key = ''.join((devicelink.CACHE_PREFIX, code))
        saved = cache.get(key)
        self.assertEqual({'name': 'test1', 'linked': False}, saved)

        status = devicelink.get_status(code)
        self.assertIsNone(status)

        devicelink.confirm_link(code)
        saved = cache.get(key)
        self.assertEqual({'name': 'test1', 'linked': True}, saved)

        status = devicelink.get_status(code)
        self.assertIsNotNone(status)
        apikey = models.ApiKey.objects.get(key=status)
        self.assertEqual('test1', apikey.device.name)

        # Entry has been deleted.
        self.assertRaises(devicelink.LinkExpiredException, devicelink.get_status,
            code)

        self.assertRaises(devicelink.LinkExpiredException, devicelink.get_status,
            'bogus-code')

    def test_build_code(self):
        code = devicelink._build_code(6)
        self.assertEqual(7, len(code))
        self.assertEqual('-', code[3])

        code = devicelink._build_code(3)
        self.assertEqual(4, len(code))
        self.assertEqual('-', code[1])
