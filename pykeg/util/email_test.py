# Copyright 2015 Kegbot Project contributors
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

"""Test for email util module."""

from builtins import str
import time
from pykeg.core import models
from pykeg.util import email

from django.test import TestCase


class EmailUtilTests(TestCase):

    def setUp(self):
        self.user = models.User.objects.create(username='email-test',
                                               email='email-test@example.com')

    def tearDown(self):
        self.user.delete()

    def test_build_email_change_token(self):
        token = email.build_email_change_token(self.user, 'new-address@example.com')
        uid, new_address = email.verify_email_change_token(self.user, token)
        self.assertEqual(self.user.id, uid)
        self.assertEqual('new-address@example.com', new_address)

    def test_expiration(self):
        token = email.build_email_change_token(self.user, 'new-address@example.com')
        time.sleep(1.1)
        try:
            email.verify_email_change_token(self.user, token, max_age=1)
            self.fail('Should have thrown exception')
        except ValueError as e:
            self.assertTrue('Signature age' in str(e))
