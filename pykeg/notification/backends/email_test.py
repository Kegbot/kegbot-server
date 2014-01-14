# Copyright 2014 Mike Wakerly <opensource@hoho.com>
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

"""Unittests for email notification backend ."""

from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from pykeg.core import models as core_models
from pykeg.core import backend
from pykeg.core import defaults
from pykeg.core import kb_common

from pykeg import notification
from pykeg.notification import models
from pykeg.notification.backends.base import BaseNotificationBackend


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
@override_settings(EMAIL_FROM_ADDRESS='test-from@example')
class EmailNotificationBackendTestCase(TestCase):
    def setUp(self):
        self.backend = backend.KegbotBackend()
        defaults.set_defaults(set_is_setup=True)

        self.user = core_models.User.objects.create(username='notification_user',
            email='test@example')

        self.prefs = models.NotificationSettings.objects.create(user=self.user,
            backend='pykeg.notification.backends.email.EmailNotificationBackend',
            keg_tapped=False, session_started=False, keg_volume_low=False,
            keg_ended=False)

    def test_keg_tapped(self):
        self.prefs.keg_tapped = True
        self.prefs.save()
        self.assertEquals(0, len(mail.outbox))

        keg = self.backend.start_keg(defaults.METER_NAME_0, beer_name='Unknown',
            brewer_name='Unknown', style_name='Unknown')
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEquals('[My Kegbot] New keg tapped: Keg 1: Unknown by Unknown', msg.subject)
        self.assertEquals(['test@example'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)

        expected_body_plain = '''A new keg of Unknown by Unknown was just tapped on My Kegbot!

Track it here: http:///kegs/1

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http:///account.'''

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = '''<p>
A new keg of <b>Unknown by Unknown</b> was just tapped on
<b><a href="http://">My Kegbot</a></b>!
</p>

<p>
Track it <a href="http:///kegs/1">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://">My Kegbot</a>.  To change your settings, visit
http:///account.
</p>'''

        self.assertEquals(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEquals('text/html', msg.alternatives[0][1])

    def test_session_started(self):
        self.prefs.session_started = True
        self.prefs.save()
        self.assertEquals(0, len(mail.outbox))
        
        keg = self.backend.start_keg(defaults.METER_NAME_0, beer_name='Unknown',
            brewer_name='Unknown', style_name='Unknown')
        drink = self.backend.record_drink(defaults.METER_NAME_0, ticks=500)
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEquals('[My Kegbot] A new session (session 1) has started.', msg.subject)
        self.assertEquals(['test@example'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)

        expected_body_plain = '''A new session was just kicked off on My Kegbot.

You can follow the session here: http:///s/1/

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http:///account.'''

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = '''<p>
A new session was just kicked off on <a href="http://">My Kegbot</a>.
</p>

<p>
You can follow the session <a href="http:///s/1/">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://">My Kegbot</a>.  To change your settings, visit
http:///account.
</p>'''

        self.assertEquals(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEquals('text/html', msg.alternatives[0][1])

    def test_keg_volume_low(self):
        self.prefs.keg_volume_low = True
        self.prefs.save()
        self.assertEquals(0, len(mail.outbox))

        keg = self.backend.start_keg(defaults.METER_NAME_0, beer_name='Unknown',
            brewer_name='Unknown', style_name='Unknown')
        drink = self.backend.record_drink(defaults.METER_NAME_0, ticks=500,
            volume_ml=keg.full_volume_ml * (1 - kb_common.KEG_VOLUME_LOW_PERCENT))
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEquals('[My Kegbot] Volume low on keg 1 (Unknown by Unknown)', msg.subject)
        self.assertEquals(['test@example'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)

        expected_body_plain = '''Keg 1 (Unknown by Unknown) is 15.0% full.

See full statistics here: http:///kegs/1

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http:///account.'''

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = '''<p>
Keg 1 (Unknown by Unknown) is <b>15.0</b>% full.
</p>

<p>
See full statistics <a href="http:///kegs/1">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://">My Kegbot</a>.  To change your settings, visit
http:///account.
</p>'''

        self.assertEquals(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEquals('text/html', msg.alternatives[0][1])

    def test_keg_ended(self):
        self.prefs.keg_ended = True
        self.prefs.save()
        self.assertEquals(0, len(mail.outbox))

        keg = self.backend.start_keg(defaults.METER_NAME_0, beer_name='Unknown',
            brewer_name='Unknown', style_name='Unknown')
        self.assertEquals(0, len(mail.outbox))
        self.backend.end_keg(defaults.METER_NAME_0)
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEquals('[My Kegbot] Keg ended: Keg 1: Unknown by Unknown', msg.subject)
        self.assertEquals(['test@example'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)

        expected_body_plain = '''Keg 1 of Unknown by Unknown was just finished on My Kegbot.

See final statistics here: http:///kegs/1

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http:///account.'''

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = '''<p>
Keg 1 (Unknown by Unknown) was just finished on
<b><a href="http://">My Kegbot</a></b>.
</p>

<p>
See final statistics <a href="http:///kegs/1">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://">My Kegbot</a>.  To change your settings, visit
http:///account.
</p>'''

        self.assertEquals(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEquals('text/html', msg.alternatives[0][1])

