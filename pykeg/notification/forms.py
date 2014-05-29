from django import forms
from pykeg.core import models


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = models.NotificationSettings
        exclude = ['user', 'backend']
