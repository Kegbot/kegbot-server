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
    new_profile, is_new = UserProfile.objects.get_or_create(user=new_user)
    new_profile.gender = self.cleaned_data['gender']
    new_profile.weight = self.cleaned_data['weight']
    new_profile.save()
    return new_user


class UserProfileForm(forms.ModelForm):
  class Meta:
    model = UserProfile
    fields = ('gender', 'weight')

