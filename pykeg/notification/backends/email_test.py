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

"""Unittests for email notification backend ."""

from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from pykeg.backend import get_kegbot_backend
from pykeg.core import models
from pykeg.core import defaults
from pykeg.core import kb_common


@override_settings(KEGBOT_BACKEND='pykeg.core.testutils.TestBackend')
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
@override_settings(EMAIL_FROM_ADDRESS='test-from@example')
class EmailNotificationBackendTestCase(TestCase):
    def setUp(self):
        self.backend = get_kegbot_backend()
        defaults.set_defaults(set_is_setup=True, create_controller=True)

        self.user = models.User.objects.create(username='notification_user',
            email='test@example')

        self.prefs = models.NotificationSettings.objects.create(user=self.user,
            backend='pykeg.notification.backends.email.EmailNotificationBackend',
            keg_tapped=False, session_started=False, keg_volume_low=False,
            keg_ended=False)

    def test_keg_tapped(self):
        self.prefs.keg_tapped = True
        self.prefs.save()
        self.assertEquals(0, len(mail.outbox))

        keg = self.backend.start_keg(defaults.METER_NAME_0, beverage_name='Unknown',
            beverage_type='beer', producer_name='Unknown', style_name='Unknown')
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEquals('[My Kegbot] New keg tapped: Keg %s: Unknown by Unknown' % keg.id,
            msg.subject)
        self.assertEquals(['test@example'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)

        expected_body_plain = '''A new keg of Unknown by Unknown was just tapped on My Kegbot!

Track it here: http://localhost:1234/kegs/%s

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http://localhost:1234/account.''' % (keg.id,)

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = '''<p>
A new keg of <b>Unknown by Unknown</b> was just tapped on
<b><a href="http://localhost:1234">My Kegbot</a></b>!
</p>

<p>
Track it <a href="http://localhost:1234/kegs/%s">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://localhost:1234">My Kegbot</a>.  To change your settings, visit
http://localhost:1234/account.
</p>''' % (keg.id,)

        self.assertEquals(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEquals('text/html', msg.alternatives[0][1])

    def test_session_started(self):
        self.prefs.session_started = True
        self.prefs.save()
        self.assertEquals(0, len(mail.outbox))

        self.backend.start_keg(defaults.METER_NAME_0, beverage_name='Unknown',
            beverage_type='beer', producer_name='Unknown', style_name='Unknown')
        drink = self.backend.record_drink(defaults.METER_NAME_0, ticks=500)
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEquals('[My Kegbot] A new session (session %s) has started.' % (
            drink.session.id,), msg.subject)
        self.assertEquals(['test@example'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)

        expected_body_plain = '''A new session was just kicked off on My Kegbot.

You can follow the session here: http://localhost:1234/s/%s

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http://localhost:1234/account.''' % (drink.session.id,)

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = '''<p>
A new session was just kicked off on <a href="http://localhost:1234">My Kegbot</a>.
</p>

<p>
You can follow the session <a href="http://localhost:1234/s/%s">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://localhost:1234">My Kegbot</a>.  To change your settings, visit
http://localhost:1234/account.
</p>''' % (drink.session.id,)

        self.assertEquals(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEquals('text/html', msg.alternatives[0][1])

    def test_keg_volume_low(self):
        self.prefs.keg_volume_low = True
        self.prefs.save()
        self.assertEquals(0, len(mail.outbox))

        keg = self.backend.start_keg(defaults.METER_NAME_0, beverage_name='Unknown',
            beverage_type='beer', producer_name='Unknown', style_name='Unknown')
        self.backend.record_drink(defaults.METER_NAME_0, ticks=500,
            volume_ml=keg.full_volume_ml * (1 - kb_common.KEG_VOLUME_LOW_PERCENT))
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEquals('[My Kegbot] Volume low on keg %s (Unknown by Unknown)' % keg.id,
            msg.subject)
        self.assertEquals(['test@example'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)

        expected_body_plain = '''Keg %s (Unknown by Unknown) is 15.0%% full.

See full statistics here: http://localhost:1234/kegs/%s

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http://localhost:1234/account.''' % (keg.id, keg.id)

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = '''<p>
Keg %s (Unknown by Unknown) is <b>15.0</b>%% full.
</p>

<p>
See full statistics <a href="http://localhost:1234/kegs/%s">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://localhost:1234">My Kegbot</a>.  To change your settings, visit
http://localhost:1234/account.
</p>''' % (keg.id, keg.id)

        self.assertEquals(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEquals('text/html', msg.alternatives[0][1])

    def test_keg_ended(self):
        self.prefs.keg_ended = True
        self.prefs.save()
        self.assertEquals(0, len(mail.outbox))

        keg = self.backend.start_keg(defaults.METER_NAME_0, beverage_name='Unknown',
            beverage_type='beer', producer_name='Unknown', style_name='Unknown')
        self.assertEquals(0, len(mail.outbox))
        self.backend.end_keg(defaults.METER_NAME_0)
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEquals('[My Kegbot] Keg ended: Keg %s: Unknown by Unknown' % keg.id, msg.subject)
        self.assertEquals(['test@example'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)

        expected_body_plain = '''Keg %s of Unknown by Unknown was just finished on My Kegbot.

See final statistics here: http://localhost:1234/kegs/%s

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http://localhost:1234/account.''' % (keg.id, keg.id)

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = '''<p>
Keg %s (Unknown by Unknown) was just finished on
<b><a href="http://localhost:1234">My Kegbot</a></b>.
</p>

<p>
See final statistics <a href="http://localhost:1234/kegs/%s">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://localhost:1234">My Kegbot</a>.  To change your settings, visit
http://localhost:1234/account.
</p>''' % (keg.id, keg.id)

        self.assertEquals(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEquals('text/html', msg.alternatives[0][1])
