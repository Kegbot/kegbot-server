from django import forms
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Hidden, Div
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from pykeg.core import models

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

class FullScreenForm(forms.Form):

    TEMPLATE_CHOICES = (
      ('taplist_carousel', 'Taplist (Carousel)'),
    )
    BACKGROUND_CHOICES = (
      ('chalkboard-bg.jpg', 'Chalkboard'),
    )

    TAP_QUERY = models.KegTap.objects.all().exclude(current_keg=None).order_by('id')
    TAP_CHOICES = [(obj.id, obj.name+': '+obj.current_keg.type.name) for obj in TAP_QUERY]
    TAP_INITIAL = [c[0] for c in TAP_CHOICES]

    template = forms.ChoiceField(choices=TEMPLATE_CHOICES, initial='taplist_carousel',
        required=True, label='Template', help_text='Please Choose a Template')
    background = forms.ChoiceField(choices=BACKGROUND_CHOICES, initial='chalkboard', 
        required=True, label='Background', help_text='Please Choose a Background Image')
    slide_rate = forms.FloatField(min_value=2.0, initial=7.5,
        required=True, label='Slide Rate', help_text='Carousel Speed (Seconds)')
    taps = forms.MultipleChoiceField(choices=TAP_CHOICES, 
        widget=forms.CheckboxSelectMultiple, initial=TAP_INITIAL,
        label='Taps', help_text='Select which taps should be displayed')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('template'),
        Field('taps'),
        Field('background'),
        Field('slide_rate'),
        FormActions(
            Submit('submit', 'Go!', css_class='btn-primary'),
        )
    )