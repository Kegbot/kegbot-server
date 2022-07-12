from builtins import object

from django import forms

from pykeg.core import models


class NotificationSettingsForm(forms.ModelForm):
    class Meta(object):
        model = models.NotificationSettings
        exclude = ["user", "backend"]
