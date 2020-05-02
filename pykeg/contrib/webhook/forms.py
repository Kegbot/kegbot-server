"""Webhook plugin forms."""

from django import forms

TEXTAREA = forms.Textarea(attrs={"class": "input-block-level"})


class SiteSettingsForm(forms.Form):
    webhook_urls = forms.CharField(
        required=False, widget=TEXTAREA, help_text="URLs for webhooks, one per line."
    )
