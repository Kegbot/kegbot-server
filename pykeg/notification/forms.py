from django import forms
from . import models


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = models.NotificationSettings
        exclude = ['user', 'backend']
