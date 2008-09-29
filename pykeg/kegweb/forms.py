from django import forms

from registration.models import RegistrationProfile
from registration.forms import RegistrationForm

from pykeg.core.models import UserProfile

class KegbotRegistrationForm(RegistrationForm):
    gender = forms.CharField()
    weight = forms.IntegerField()

    def save(self, profile_callback=None):
        new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'],
                                                                    send_email=False,
                                                                    profile_callback=profile_callback)
        new_user.is_active = True
        new_user.save()
        new_profile = UserProfile.objects.create(user=new_user,
          gender=self.cleaned_data['gender'],
          weight=self.cleaned_data['weight'])
        new_profile.save()
        return new_user


