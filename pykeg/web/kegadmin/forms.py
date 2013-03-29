from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Hidden, Div
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from pykeg.core import models

ALL_TAPS = models.KegTap.objects.all()
ALL_SIZES = models.KegSize.objects.all()
ALL_KEGS = models.Keg.objects.all()

class GeneralSettingsForm(forms.Form):
  name = forms.CharField(help_text='Name of this Kegbot system')

class ChangeKegForm(forms.Form):
  keg_size = forms.ModelChoiceField(queryset=ALL_SIZES,
      required=True,
      empty_label=None)

  beer_name = forms.CharField(required=True, label='Beer Name')
  beer_id = forms.CharField(widget=forms.HiddenInput(), required=False)
  brewer_name = forms.CharField(required=True, label='Brewer')
  brewer_id = forms.CharField(widget=forms.HiddenInput(), required=False)
  style_name = forms.CharField(required=True, label='Style',
    help_text='Example: Pale Ale, Stout, etc.')
  style_id = forms.CharField(widget=forms.HiddenInput(), required=False)

  description = forms.CharField(required=False,
      help_text='Public description of this specific keg (optional)')

  helper = FormHelper()
  helper.form_class = 'form-horizontal beer-select'
  helper.layout = Layout(
      Field('beer_name', css_class='input-xlarge'),
      Field('beer_id', type='hidden'),
      Field('brewer_name', css_class='input-xlarge'),
      Field('brewer_id', type='hidden'),
      Field('style_name', css_class='input-xlarge'),
      Field('style_id', type='hidden'),
      Field('keg_size', css_class='input-xlarge'),
      Field('description', css_class='input-xlarge'),
      FormActions(
          Submit('submit_change_keg_form', 'Activate Keg', css_class='btn-primary'),
      )
  )

class EndKegForm(forms.Form):
  keg = forms.ModelChoiceField(queryset=ALL_KEGS, widget=forms.HiddenInput)

  helper = FormHelper()
  helper.form_class = 'form-horizontal beer-select'
  helper.layout = Layout(
      Field('keg', type='hidden'),
      FormActions(
        Submit('submit_end_keg_form', 'End Keg', css_class='btn-danger'),
      )
  )


class TapForm(forms.ModelForm):
  class Meta:
    model = models.KegTap
    fields = ('name', 'meter_name', 'relay_name', 'description',
        'temperature_sensor', 'ml_per_tick')

  def __init__(self, *args, **kwargs):
    site = kwargs.pop('site', None)
    super(TapForm, self).__init__(*args, **kwargs)
    self.fields['temperature_sensor'].queryset = models.ThermoSensor.objects.filter(site=site)
    self.fields['temperature_sensor'].empty_label = 'No sensor.'

  helper = FormHelper()
  helper.form_class = 'form-horizontal'
  helper.layout = Layout(
      Field('name', css_class='input-xlarge'),
      Field('meter_name', css_class='input-xlarge'),
      Field('relay_name', css_class='input-xlarge'),
      Field('temperature_sensor', css_class='input-xlarge'),
      Field('ml_per_tick', css_class='input-xlarge'),
      Field('description', css_class='input-xlarge'),
      FormActions(
          Submit('submit_tap_form', 'Save Settings', css_class='btn-success'),
      )
  )


class DeleteTapForm(forms.Form):
  helper = FormHelper()
  helper.form_class = 'form-horizontal'
  helper.layout = Layout(
      FormActions(
          Submit('submit_delete_tap_form', 'Delete Tap', css_class='btn-danger'),
      )
  )


class SiteSettingsForm(forms.ModelForm):
  class Meta:
    model = models.SiteSettings
    fields = (
        'title',
        'description',
        'privacy',
        'volume_display_units',
        'temperature_display_units',
        'event_web_hook',
        'session_timeout_minutes',
        'google_analytics_id',
        'guest_name',
        'guest_image',
        'default_user',
        'registration_allowed',
        'registration_confirmation',
        'allowed_hosts',
    )

  helper = FormHelper()
  helper.form_class = 'form-horizontal'
  helper.layout = Layout(
      Field('title', css_class='input-xlarge'),
      Field('description', css_class='input-xlarge'),
      Field('privacy', css_class='input-xlarge'),
      Field('volume_display_units', css_class='input-xlarge'),
      Field('temperature_display_units', css_class='input-xlarge'),
      Field('event_web_hook', css_class='input-xlarge'),
      Field('session_timeout_minutes'),
      Field('google_analytics_id'),
      Field('guest_name'),
      Field('guest_image'),
      Field('default_user'),
      Field('registration_allowed', css_class='input-xlarge'),
      Field('registration_confirmation', css_class='input-xlarge'),
      Field('allowed_hosts'),
      FormActions(
          Submit('submit', 'Save Settings', css_class='btn-primary'),
      )
  )

#BeerTypeFormSet = inlineformset_factory(models.Brewer, models.BeerType)

class TweetForm(forms.Form):
  tweet = forms.CharField(max_length=140, required=True)

class FindUserForm(forms.Form):
  username = forms.CharField()

class UserForm(forms.ModelForm):
  class Meta:
    model = models.User
    fields = (
        'username',
        'email',
        'password',
        'is_staff',
    )

  helper = FormHelper()
  helper.form_class = 'form-horizontal'
  helper.layout = Layout(
      Field('username', css_class='input-xlarge'),
      Field('email', css_class='input-xlarge'),
      'password',
      'is_staff',
      FormActions(
          Submit('submit', 'Save', css_class='btn-primary'),
      )
  )

