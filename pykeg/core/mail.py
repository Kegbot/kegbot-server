import logging

import dj_email_url
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend
from django.core.mail.backends.dummy import EmailBackend as DummyEmailBackend
from django.core.mail.backends.locmem import EmailBackend as LocmemEmailBackend
from django.core.mail.backends.smtp import EmailBackend as SmtpEmailBackend

from . import models

logger = logging.getLogger(__name__)


class KegbotEmailBackend(BaseEmailBackend):
    """Email backend which uses KegbotSite.email_config

    This backend allows users to set/manage their email settings through the
    database instead of the environment.

    If the site is not setup, the console will be used.
    """

    def _get_default_from_email(self):
        """Try to determine the `From` address from site settings."""
        site = models.KegbotSite.get()
        from_email = None
        if site.is_setup:
            from_email = dj_email_url.parse(site.email_config).get("DEFAULT_FROM_EMAIL")
        if not from_email:
            logger.warning(
                "Default 'From:' email is not configured, using: {settings.DEFAULT_FROM_EMAIL}"
            )
            from_email = settings.DEFAULT_FROM_EMAIL
        return from_email

    def _get_impl(self):
        """Try to get a concrete email backend implementation from site settings."""
        site = models.KegbotSite.get()
        if not site.is_setup:
            logger.warning("Site is not setup, returning console email backend.")
            return ConsoleEmailBackend()

        config = dj_email_url.parse(site.email_config)
        logger.debug(f"Email config: {config}")

        parsed_backend = config.get("EMAIL_BACKEND")
        if parsed_backend == "django.core.mail.backends.dummy.EmailBackend":
            logger.debug("Configured for dummy email backend")
            return DummyEmailBackend()
        elif parsed_backend == "django.core.mail.backends.console.EmailBackend":
            logger.debug("Configured for console email backend")
            return ConsoleEmailBackend()
        elif parsed_backend == "django.core.mail.backends.locmem.EmailBackend":
            logger.debug("Configured for local memory email backend")
            return LocmemEmailBackend()

        if parsed_backend != "django.core.mail.backends.smtp.EmailBackend":
            raise ImproperlyConfigured(f"Unexpected email backend: {parsed_backend}")

        smtp_settings = {
            "host": config.get("EMAIL_HOST"),
            "port": config.get("EMAIL_PORT"),
            "username": config.get("EMAIL_HOST_USER"),
            "password": config.get("EMAIL_HOST_PASSWORD"),
            "use_tls": config.get("EMAIL_USE_TLS"),
            "fail_silently": False,
            "use_ssl": config.get("EMAIL_USE_SSL"),
            "timeout": config.get("EMAIL_TIMEOUT"),
            "ssl_keyfile": config.get("EMAIL_SSL_KEYFILE"),
            "ssl_certfile": config.get("EMAIL_SSL_CERTFILE"),
        }
        logger.debug(f"Configured for SMTP, settings={smtp_settings}")

        return SmtpEmailBackend(**smtp_settings)

    def open(self):
        """EmailBackend method: Open a connection."""
        return self._get_impl().open()

    def close(self):
        """EmailBackend method: Close a connection."""
        return self._get_impl().close()

    def send_messages(self, email_messages):
        """EmailBackend method: Send messages."""
        configured_default_from_email = self._get_default_from_email()
        for message in email_messages:
            # If callers don't specify a `from_email`, or if they used
            # `settings.DEFAULT_FROM_EMAIL` which is by default invalid, try to
            # replace it with the value from site config.
            if not message.from_email or message.from_email == settings.DEFAULT_FROM_EMAIL:
                message.from_email = configured_default_from_email
        return self._get_impl().send_messages(email_messages)
