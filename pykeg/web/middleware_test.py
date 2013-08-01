# Copyright 2012 Mike Wakerly <opensource@hoho.com>
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

'''Tests for middleware.py.'''

import unittest

from . import middleware

class MiddlewareTestCase(unittest.TestCase):
    def test_validate_host(self):
        allowed_hosts = []
        self.assertTrue(middleware.HttpHostMiddleware.validate_host('foo', allowed_hosts))

        allowed_hosts = ['blort', '*']
        self.assertTrue(middleware.HttpHostMiddleware.validate_host('foo', allowed_hosts))

        allowed_hosts = ['blort']
        self.assertFalse(middleware.HttpHostMiddleware.validate_host('foo', allowed_hosts))

        # Patterns are not supported.. yet.
        allowed_hosts = ['*.bar.com']
        self.assertFalse(middleware.HttpHostMiddleware.validate_host('foo.bar.com', allowed_hosts))
