from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    next_page = forms.CharField(required=False, widget=forms.HiddenInput)


class MugshotForm(forms.Form):
    new_mugshot = forms.ImageField(required=True)


class RegenerateApiKeyForm(forms.Form):
    pass
