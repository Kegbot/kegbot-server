"""Django forms reused by API endpoints."""

import urllib.parse

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from pykeg.core import models
from pykeg.web.util import get_base_url

User = get_user_model()


class PasswordResetForm(forms.Form):
    """Builds and mails password-reset links (relocated from the old
    registration app; the reset link lands on a frontend route)."""

    email = forms.EmailField(max_length=254)

    def save(
        self,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        **kwargs,
    ):
        """Generates a one-use only link for resetting password and sends
        it to the user."""
        from django.core.mail import send_mail

        email = self.cleaned_data["email"]
        active_users = User._default_manager.filter(email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable.
            if not user.has_usable_password():
                continue
            from_email = settings.DEFAULT_FROM_EMAIL or from_email

            base_url = get_base_url()
            parsed = urllib.parse.urlparse(base_url)

            kbsite = models.KegbotSite.get()
            context = {
                "email": user.email,
                "site_name": kbsite.title,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "domain": parsed.netloc,
                "protocol": parsed.scheme,
            }
            subject = loader.render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines.
            subject = "".join(subject.splitlines())
            body = loader.render_to_string(email_template_name, context)
            send_mail(subject, body, from_email, [user.email])
