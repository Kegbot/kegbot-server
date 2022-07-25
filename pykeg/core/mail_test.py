from django.core import mail as django_mail
from django.core.mail import get_connection, send_mail
from django.test import TestCase
from django.test.utils import override_settings

from . import mail, models


@override_settings(EMAIL_BACKEND="pykeg.core.mail.KegbotEmailBackend")
class KegbotEmailBackendTests(TestCase):
    fixtures = ["testdata/demo-site.json"]

    def test_default_backend_is_console(self):
        backend = get_connection()
        self.assertIsInstance(backend, mail.KegbotEmailBackend)
        impl = backend._get_impl()
        self.assertIsInstance(impl, mail.ConsoleEmailBackend)

    def test_smtp_config(self):
        site = models.KegbotSite.get()
        site.email_config = (
            "submission://user:secret@example.com:1234/?_default_from_email=yo@example.com"
        )
        site.save()
        backend = get_connection()
        self.assertIsInstance(backend, mail.KegbotEmailBackend)
        impl = backend._get_impl()
        self.assertIsInstance(impl, mail.SmtpEmailBackend)
        self.assertEqual(1234, impl.port)
        self.assertEqual("example.com", impl.host)
        self.assertEqual(True, impl.use_tls)
        self.assertEqual(False, impl.use_ssl)
        self.assertEqual("yo@example.com", backend._get_default_from_email())

    def test_sends_emails_to_locmem(self):
        site = models.KegbotSite.get()
        site.email_config = "memory://?_default_from_email=test@example.com"
        site.save()

        backend = get_connection()
        self.assertIsInstance(backend, mail.KegbotEmailBackend)
        self.assertEqual("test@example.com", backend._get_default_from_email())

        impl = backend._get_impl()
        self.assertIsInstance(impl, mail.LocmemEmailBackend)

        send_mail("Test subject", "Hello world.", None, ["to@example.com"])
        self.assertEqual(len(django_mail.outbox), 1)
        self.assertEqual(django_mail.outbox[0].subject, "Test subject")
        self.assertEqual(django_mail.outbox[0].from_email, "test@example.com")
