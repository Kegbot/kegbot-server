from django.http import Http404
from django.conf import settings
from django.template.loader import render_to_string

from registration.models import RegistrationProfile
from registration.views import RegistrationView as BaseRegistrationView
from registration.backends.simple.views import RegistrationView as SimpleRegistrationView
from registration.backends.default.views import RegistrationView as DefaultRegistrationView

from pykeg.core import models

def send_activation_email(self, site):
    """
    Monkey-patched version of RegistrationProfile method, which
    adds Kegbot-specific context variables.
    """
    s = models.SiteSettings.get()
    site_name = s.title
    base_url = s.base_url()

    print 'send_activation_email', self.activation_key

    ctx_dict = {'activation_key': self.activation_key,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                'site': site,
                'site_name': site_name,
                'base_url': base_url}
    subject = render_to_string('registration/activation_email_subject.txt',
                               ctx_dict)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    message = render_to_string('registration/activation_email.txt',
                               ctx_dict)
    self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

RegistrationProfile.send_activation_email = send_activation_email


class RegistrationView(BaseRegistrationView):
    def __init__(self):
        self._simple = SimpleRegistrationView()
        self._default = DefaultRegistrationView()

    def _get_view(self, request):
        settings = request.kbsite.settings
        if not settings.registration_allowed:
            raise Http404('Registration is disabled.')
        if settings.registration_confirmation:
            return self._default
        else:
            return self._simple

    def get_success_url(self, request, user):
        settings = request.kbsite.settings
        if settings.registration_confirmation:
            return ('registration_complete', (), {})
        else:
            return 'kb-account-main'

    def registration_allowed(self, request):
        settings = request.kbsite.settings
        return settings.registration_allowed

    def register(self, request, **cleaned_data):
        return self._get_view(request).register(request, **cleaned_data)
