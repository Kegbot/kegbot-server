# Copyright 2013 Mike Wakerly <opensource@hoho.com>
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

"""General tests for the web interface."""

from django.test import TransactionTestCase
from pykeg.core import backend
from pykeg.core import models
from pykeg.core import defaults

class KegwebTestCase(TransactionTestCase):
    def setUp(self):
        defaults.set_defaults(set_is_setup=True)

    def testBasicEndpoints(self):
        for endpoint in ('/kegs/', '/stats/'):
            response = self.client.get(endpoint)
            self.assertEquals(200, response.status_code)

        for endpoint in ('/sessions/',):
            response = self.client.get(endpoint)
            self.assertEquals(404, response.status_code)

        b = backend.KegbotBackend()
        keg = b.start_keg('kegboard.flow0', beer_name='Unknown', brewer_name='Unknown',
            style_name='Unknown')
        self.assertIsNotNone(keg)
        response = self.client.get('/kegs/')
        self.assertEquals(200, response.status_code)

        d = b.record_drink('kegboard.flow0', ticks=100)
        drink_id = d.id

        response = self.client.get('/d/%s' % drink_id, follow=True)
        self.assertRedirects(response, '/drinks/%s' % drink_id, status_code=301)

        session_id = d.session.id
        response = self.client.get('/s/%s' % session_id, follow=True)
        self.assertRedirects(response, d.session.get_absolute_url(), status_code=301)

    def testShout(self):
        b = backend.KegbotBackend()
        keg = b.start_keg('kegboard.flow0', beer_name='Unknown', brewer_name='Unknown',
            style_name='Unknown')
        d = b.record_drink('kegboard.flow0', ticks=123, shout='_UNITTEST_')
        response = self.client.get(d.get_absolute_url())
        self.assertContains(response, '<p>_UNITTEST_</p>', status_code=200)
