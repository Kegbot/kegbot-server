from django import forms
from django.contrib.auth.forms import AuthenticationForm

from registration.models import RegistrationProfile
from registration.forms import RegistrationForm

from pykeg.core import models

class LoginForm(AuthenticationForm):
    next_page = forms.CharField(required=False, widget=forms.HiddenInput)


class KegbotRegistrationForm(RegistrationForm):
    def save(self, profile_callback=None):
        new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'],
                                                                    send_email=False,
                                                                    profile_callback=profile_callback)
        new_user.is_active = True
        new_user.save()
        return new_user


class MugshotForm(forms.Form):
    new_mugshot = forms.ImageField(required=True)


class RegenerateApiKeyForm(forms.Form):
    pass
