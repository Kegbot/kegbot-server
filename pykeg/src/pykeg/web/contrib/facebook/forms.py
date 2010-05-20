from django import forms
from pykeg.contrib.facebook import models as facebook_models

class FacebookSettingsForm(forms.ModelForm):
  class Meta:
    model = facebook_models.FacebookSettings
    exclude = ('profile',)

class WallPostForm(forms.Form):
  message = forms.CharField()
