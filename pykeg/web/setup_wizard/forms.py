# Copyright 2013 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from pykeg.core import models

class CreateOrImportForm(forms.Form):
  CHOICES = (
      ('create', 'Create New System'),
      ('import', 'Import From Backup'),
  )
  mode = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
  import_file  = forms.FileField(required=False)

  helper = FormHelper()
  helper.form_class = 'setup-form span8 offset2'
  helper.layout = Layout(
      Field('mode', css_class='input-xlarge'),
      Field('import_file', css_class='input-xlarge'),
      FormActions(
          Submit('save_changes', 'Continue', css_class="btn-primary"),
      )
  )


class MiniSiteSettingsForm(forms.ModelForm):
  class Meta:
    model = models.SiteSettings
    fields = (
        'title',
        'privacy',
        'volume_display_units',
        'temperature_display_units',
        'registration_allowed',
        'registration_confirmation',
    )
    widgets = {
        'privacy': forms.RadioSelect(),
        'volume_display_units': forms.RadioSelect(),
        'temperature_display_units': forms.RadioSelect(),
    }

  helper = FormHelper()
  helper.form_class = 'setup-form span8 offset2'
  helper.layout = Layout(
      Field('title', css_class='span12'),
      Field('privacy', css_class='span12'),
      Field('volume_display_units', css_class='span12'),
      Field('temperature_display_units', css_class='span12'),
      Field('registration_allowed'),
      Field('registration_confirmation'),
      FormActions(
          Submit('save_changes', 'Continue', css_class="btn-primary"),
      )
  )

class AdminUserForm(forms.Form):
  username = forms.RegexField(
      label='Username',
      max_length=30,
      regex=r'^[\w-]+$',
      help_text='Your username: 30 characters or fewer. Alphanumeric characters only (letters, digits, hyphens and underscores).',
      error_message='Must contain only letters, numbers, hyphens and underscores.')

  password = forms.CharField(widget=forms.PasswordInput())
  confirm_password = forms.CharField(widget=forms.PasswordInput())
  email = forms.EmailField(
      help_text='In case you lose your password.')

  helper = FormHelper()
  helper.form_class = 'setup-form span8 offset2'
  helper.layout = Layout(
      Field('username', css_class='span12'),
      Field('email', css_class='span12'),
      Field('password', css_class='span12'),
      Field('confirm_password', css_class='span12'),
      FormActions(
          Submit('save_changes', 'Continue', css_class="btn-primary"),
      )
  )

  def clean_confirm_password(self):
    orig = self.cleaned_data.get('password')
    confirm = self.cleaned_data.get('confirm_password')
    if orig and confirm and orig != confirm:
      raise forms.ValidationError('Passwords must match!')
    return confirm

  def clean_username(self):
    username = self.cleaned_data.get('username')
    if username:
      try:
        models.User.objects.get(username=username)
        raise forms.ValidationError('Sorry, this username is taken already?!')
      except models.User.DoesNotExist:
        pass  # expected
    return username

  def save(self):
    u = models.User()
    u.username = self.cleaned_data.get('username')
    u.email = self.cleaned_data.get('email')
    u.is_staff = True
    u.is_superuser = True
    u.save()
    u.set_password(self.cleaned_data.get('password'))
    u.save()
    return u

