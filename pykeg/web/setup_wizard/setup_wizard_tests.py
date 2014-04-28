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

"""Unittests for setup wizard."""

from django.core.cache import cache
from django.test import TransactionTestCase
from django.test.utils import override_settings

from pykeg.core import defaults


class SetupWizardTestCase(TransactionTestCase):

    def setUp(self):
        cache.clear()

    def test_settings_debug_false(self):
        """Verify wizard is not offered (DEBUG is False)."""
        for path in ('/', '/stats/'):
            response = self.client.get(path)
            self.assertContains(response, '<h2>Kegbot Offline</h2>',
                status_code=403)
            self.assertNotContains(response, 'Start Setup',
                status_code=403)

        response = self.client.get('/setup/')
        self.failUnlessEqual(response.status_code, 404)

    @override_settings(DEBUG=True)
    def test_settings_debug_true(self):
        """Verify wizard is offered (DEBUG is True)."""
        for path in ('/', '/stats/'):
            response = self.client.get(path)
            self.assertContains(response, '<h2>Setup Required</h2>', status_code=403)
            self.assertContains(response, 'Start Setup', status_code=403)

        response = self.client.get('/setup/')
        self.failUnlessEqual(response.status_code, 200)

    def test_setup_not_shown(self):
        """Verify wizard is not shown on set-up site."""
        site = defaults.set_defaults()
        site.is_setup = True
        site.save()
        for path in ('/', '/stats/'):
            response = self.client.get(path)
            self.assertNotContains(response, '<h2>Kegbot Offline</h2>',
                status_code=200)
            self.assertNotContains(response, '<h2>Setup Required</h2>',
                status_code=200)
            self.assertNotContains(response, 'Start Setup', status_code=200)

        response = self.client.get('/setup/')
        self.failUnlessEqual(response.status_code, 404)
