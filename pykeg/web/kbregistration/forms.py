import urllib.parse
from builtins import object

from django import forms
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from pykeg.web.util import get_base_url

try:
    from django.contrib.auth import get_user_model

    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

from pykeg.core import models


class KegbotRegistrationForm(forms.ModelForm):
    class Meta(object):
        model = models.User
        fields = ("email", "username")

    password1 = forms.CharField(widget=forms.PasswordInput, label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput, label=_("Password (again)"))

    def clean(self):
        super(KegbotRegistrationForm, self).clean()
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail

        email = self.cleaned_data["email"]
        active_users = User._default_manager.filter(email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            from_email = settings.DEFAULT_FROM_EMAIL or from_email

            base_url = get_base_url()
            parsed = urllib.parse.urlparse(base_url)
            domain = parsed.netloc
            protocol = parsed.scheme

            kbsite = models.KegbotSite.get()
            site_name = kbsite.title
            c = {
                "email": user.email,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "domain": domain,
                "protocol": protocol,
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = "".join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [user.email])
