import datetime

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.db import transaction

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now

from registration.models import RegistrationManager
from pykeg.core.models import KegbotSite

class KegbotRegistrationManager(RegistrationManager):
    def create_inactive_user(self, username, email, password,
                             send_email=True):
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email()

        return new_user
    create_inactive_user = transaction.commit_on_success(create_inactive_user)


class KegbotRegistrationProfile(models.Model):
    """
    Clone of registration's models.RegistrationProfile, with support
    for custom user model.
    """
    ACTIVATED = u"ALREADY_ACTIVATED"

    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    activation_key = models.CharField(_('activation key'), max_length=40)

    objects = KegbotRegistrationManager()

    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')

    def __unicode__(self):
        return u"Registration information for %s" % self.user

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime_now())
    activation_key_expired.boolean = True

    def send_activation_email(self):
        """Adds Kegbot-specific context variables."""
        s = KegbotSite.get()
        site_name = s.title
        base_url = s.base_url()

        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site_name': site_name,
                    'base_url': base_url}
        subject = render_to_string('registration/activation_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        message = render_to_string('registration/activation_email.txt',
                                   ctx_dict)
        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
