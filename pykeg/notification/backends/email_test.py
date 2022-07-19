"""Unittests for email notification backend ."""

from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

from pykeg.core import defaults, kb_common, models


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
@override_settings(DEFAULT_FROM_EMAIL="test-from@example")
class EmailNotificationBackendTestCase(TestCase):
    def setUp(self):
        defaults.set_defaults(set_is_setup=True, create_controller=True)

        self.user = models.User.objects.create(username="notification_user", email="test@example")

        self.prefs = models.NotificationSettings.objects.create(
            user=self.user,
            backend="pykeg.notification.backends.email.EmailNotificationBackend",
            keg_tapped=False,
            session_started=False,
            keg_volume_low=False,
            keg_ended=False,
        )

    def test_keg_tapped(self):
        self.prefs.keg_tapped = True
        self.prefs.save()
        self.assertEqual(0, len(mail.outbox))

        keg = models.Keg.start_keg(
            defaults.METER_NAME_0,
            beverage_name="Unknown",
            beverage_type="beer",
            producer_name="Unknown",
            style_name="Unknown",
        )
        self.assertEqual(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEqual(
            "[My Kegbot] New keg tapped: Keg %s: Unknown by Unknown" % keg.id, msg.subject
        )
        self.assertEqual(["test@example"], msg.to)
        self.assertEqual("test-from@example", msg.from_email)

        expected_body_plain = """A new keg of Unknown by Unknown was just tapped on My Kegbot!

Track it here: http://test.example.com/kegs/%s/

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http://test.example.com/account.""" % (
            keg.id,
        )

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = """<p>
A new keg of <b>Unknown by Unknown</b> was just tapped on
<b><a href="http://test.example.com">My Kegbot</a></b>!
</p>

<p>
Track it <a href="http://test.example.com/kegs/%s/">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://test.example.com">My Kegbot</a>.  To change your settings, visit
http://test.example.com/account.
</p>""" % (
            keg.id,
        )

        self.assertEqual(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEqual("text/html", msg.alternatives[0][1])

    def test_session_started(self):
        self.prefs.session_started = True
        self.prefs.save()
        self.assertEqual(0, len(mail.outbox))

        models.Keg.start_keg(
            defaults.METER_NAME_0,
            beverage_name="Unknown",
            beverage_type="beer",
            producer_name="Unknown",
            style_name="Unknown",
        )
        drink = models.Drink.record_drink(defaults.METER_NAME_0, ticks=500)
        self.assertEqual(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEqual(
            "[My Kegbot] A new session (session %s) has started." % (drink.session.id,), msg.subject
        )
        self.assertEqual(["test@example"], msg.to)
        self.assertEqual("test-from@example", msg.from_email)

        expected_body_plain = """A new session was just kicked off on My Kegbot.

You can follow the session here: http://test.example.com/s/%s/

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http://test.example.com/account.""" % (
            drink.session.id,
        )

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = """<p>
A new session was just kicked off on <a href="http://test.example.com">My Kegbot</a>.
</p>

<p>
You can follow the session <a href="http://test.example.com/s/%s/">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://test.example.com">My Kegbot</a>.  To change your settings, visit
http://test.example.com/account.
</p>""" % (
            drink.session.id,
        )

        self.assertEqual(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEqual("text/html", msg.alternatives[0][1])

    def test_keg_volume_low(self):
        self.prefs.keg_volume_low = True
        self.prefs.save()
        self.assertEqual(0, len(mail.outbox))

        keg = models.Keg.start_keg(
            defaults.METER_NAME_0,
            beverage_name="Unknown",
            beverage_type="beer",
            producer_name="Unknown",
            style_name="Unknown",
        )
        models.Drink.record_drink(
            defaults.METER_NAME_0,
            ticks=500,
            volume_ml=keg.full_volume_ml * (1 - kb_common.KEG_VOLUME_LOW_PERCENT),
        )
        self.assertEqual(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEqual(
            "[My Kegbot] Volume low on keg %s (Unknown by Unknown)" % keg.id, msg.subject
        )
        self.assertEqual(["test@example"], msg.to)
        self.assertEqual("test-from@example", msg.from_email)

        expected_body_plain = """Keg %s (Unknown by Unknown) is 15.0%% full.

See full statistics here: http://test.example.com/kegs/%s/

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http://test.example.com/account.""" % (
            keg.id,
            keg.id,
        )

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = """<p>
Keg %s (Unknown by Unknown) is <b>15.0</b>%% full.
</p>

<p>
See full statistics <a href="http://test.example.com/kegs/%s/">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://test.example.com">My Kegbot</a>.  To change your settings, visit
http://test.example.com/account.
</p>""" % (
            keg.id,
            keg.id,
        )

        self.assertEqual(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEqual("text/html", msg.alternatives[0][1])

    def test_keg_ended(self):
        self.prefs.keg_ended = True
        self.prefs.save()
        self.assertEqual(0, len(mail.outbox))

        keg = models.Keg.start_keg(
            defaults.METER_NAME_0,
            beverage_name="Unknown",
            beverage_type="beer",
            producer_name="Unknown",
            style_name="Unknown",
        )
        self.assertEqual(0, len(mail.outbox))
        keg.current_tap.end_current_keg()
        self.assertEqual(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEqual("[My Kegbot] Keg ended: Keg %s: Unknown by Unknown" % keg.id, msg.subject)
        self.assertEqual(["test@example"], msg.to)
        self.assertEqual("test-from@example", msg.from_email)

        expected_body_plain = """Keg %s of Unknown by Unknown was just finished on My Kegbot.

See final statistics here: http://test.example.com/kegs/%s/

You are receiving this e-mail because you have notifications enabled
on My Kegbot.  To change your settings, visit http://test.example.com/account.""" % (
            keg.id,
            keg.id,
        )

        self.assertMultiLineEqual(expected_body_plain, msg.body)

        expected_body_html = """<p>
Keg %s (Unknown by Unknown) was just finished on
<b><a href="http://test.example.com">My Kegbot</a></b>.
</p>

<p>
See final statistics <a href="http://test.example.com/kegs/%s/">here</a>.
</p>

<p>
You are receiving this e-mail because you have notifications enabled
on <a href="http://test.example.com">My Kegbot</a>.  To change your settings, visit
http://test.example.com/account.
</p>""" % (
            keg.id,
            keg.id,
        )

        self.assertEqual(1, len(msg.alternatives))
        self.assertMultiLineEqual(expected_body_html, msg.alternatives[0][0])
        self.assertEqual("text/html", msg.alternatives[0][1])
