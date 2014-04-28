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

from django.contrib.auth import authenticate
from django.contrib.auth import login

from registration import signals
from registration.views import ActivationView as BaseActivationView
from registration.views import RegistrationView as BaseRegistrationView

from pykeg.web.kbregistration.forms import KegbotRegistrationForm
from pykeg.web.kbregistration.models import KegbotRegistrationProfile

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

"""Kegbot-aware clone of django-registration default backend views."""


class RegistrationView(BaseRegistrationView):
    """Hybrid of backends.default and backends.simple.

    The register() method considers SiteSettings in deciding whether
    to immediately activate the new account or send an activation_key
    email.

    All methods use KegbotRegistrationProfile rather than
    django-registration's built-in profile since the latter is not
    aware of our custom User.
    """
    form_class = KegbotRegistrationForm

    def register(self, request, **cleaned_data):
        settings = request.kbsite

        username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']

        if settings.registration_confirmation:
            new_user = KegbotRegistrationProfile.objects.create_inactive_user(
                username, email, password)
        else:
            User.objects.create_user(username, email, password)
            new_user = authenticate(username=username, password=password)
            login(request, new_user)

        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user

    def registration_allowed(self, request):
        return request.kbsite.registration_allowed

    def get_success_url(self, request, user):
        if request.kbsite.registration_confirmation:
            return ('registration_complete', (), {})
        else:
            return 'kb-account-main'


class ActivationView(BaseActivationView):
    def activate(self, request, activation_key):
        activated_user = KegbotRegistrationProfile.objects.activate_user(activation_key)
        if activated_user:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated_user,
                                        request=request)
        return activated_user

    def get_success_url(self, request, user):
        return ('registration_activation_complete', (), {})
