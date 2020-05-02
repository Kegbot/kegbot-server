"""Untappd plugin forms."""

from django import forms

WIDE_TEXT = forms.TextInput(attrs={"class": "input-block-level"})


class SiteSettingsForm(forms.Form):
    client_id = forms.CharField(
        required=False, widget=WIDE_TEXT, help_text="Untappd API Client ID."
    )
    client_secret = forms.CharField(
        required=False, widget=WIDE_TEXT, help_text="Untappd API Client Secret"
    )


class UserSettingsForm(forms.Form):
    enable_checkins = forms.BooleanField(
        initial=True, required=False, help_text="Check in when you join a session."
    )
