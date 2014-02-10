from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    next_page = forms.CharField(required=False, widget=forms.HiddenInput)


class ActivateAccountForm(forms.Form):
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2

class MugshotForm(forms.Form):
    new_mugshot = forms.ImageField(required=True)


class RegenerateApiKeyForm(forms.Form):
    pass
