from django import forms
from django.conf import settings

from registration.models import RegistrationProfile
from registration.forms import RegistrationForm

from pykeg.core import models

class KegbotRegistrationForm(RegistrationForm):
  WEIGHT_CHOICES = (
      (100, 'less than 100'),
      (120, '100-130'),
      (150, '131-170'),
      (180, '171+'),
  )
  GENDER_CHOICES = (
      ('male', 'Male'),
      ('female', 'Female'),
  )
  gender = forms.ChoiceField(choices=GENDER_CHOICES,
      help_text='Used for BAC estimation.')
  weight = forms.ChoiceField(choices=WEIGHT_CHOICES,
      help_text='Used for BAC estimation, kept private. You can lie.')
  twitter_name = forms.CharField(required=False,
      help_text='Do you use twitter? Enter your twitter name here to enable '
        'tweets announcing your drinks.')

  def save(self, profile_callback=None):
    new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                password=self.cleaned_data['password1'],
                                                                email=self.cleaned_data['email'],
                                                                send_email=False,
                                                                profile_callback=profile_callback)
    new_user.is_active = True
    new_user.save()
    new_profile, is_new = models.UserProfile.objects.get_or_create(user=new_user)
    new_profile.gender = self.cleaned_data['gender']
    new_profile.weight = self.cleaned_data['weight']
    new_profile.save()

    if 'pykeg.contrib.twitter' in settings.INSTALLED_APPS:
      twitter_name = self.cleaned_data.get('twitter_name')
      if twitter_name:
        from pykeg.contrib.twitter import models as twitter_models
        link = twitter_models.UserTwitterLink()
        link.user_profile = new_profile
        link.twitter_name = twitter_name
        link.save()

    return new_user


class UserProfileForm(forms.ModelForm):
  class Meta:
    model = models.UserProfile
    fields = ('gender', 'weight')


class MugshotForm(forms.Form):
  new_mugshot = forms.ImageField(required=False)


UNASSIGNED_TOKEN_QS = models.AuthenticationToken.objects.filter(user=None)
NEW_USERS = models.User.objects.all().order_by('-date_joined')

class ClaimTokenForm(forms.Form):
  token = forms.ModelChoiceField(queryset=UNASSIGNED_TOKEN_QS)
  user = forms.ModelChoiceField(queryset=NEW_USERS)
