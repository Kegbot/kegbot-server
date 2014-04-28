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

"""Unittests for registration functions."""

from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from pykeg.backend import get_kegbot_backend
from pykeg.core import models as core_models
from pykeg.core import defaults


class ForgotPasswordTest(TestCase):
    def setUp(self):
        self.backend = get_kegbot_backend()
        defaults.set_defaults(set_is_setup=True)

        self.user = core_models.User.objects.create(username='notification_user',
            email='test@example.com')

        # Password reset requires a usable password.
        self.user.set_password('1234')
        self.user.save()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @override_settings(EMAIL_FROM_ADDRESS='test-from@example')
    def test_notifications(self):
        response = self.client.get('/accounts/password/reset/')
        self.assertContains(response, "Reset Password", status_code=200)
        self.assertEquals(0, len(mail.outbox))

        response = self.client.post('/accounts/password/reset/', data={'email': 'test@example.com'},
            follow=True)
        self.assertContains(response, 'E-Mail Sent', status_code=200)
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]

        self.assertEquals('Password reset on My Kegbot', msg.subject)
        self.assertEquals(['test@example.com'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)
