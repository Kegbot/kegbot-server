from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Hidden, Div
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from kegbot.util import units
from pykeg.core import backend
from pykeg.core import keg_sizes
from pykeg.core import models

ALL_TAPS = models.KegTap.objects.all()
ALL_KEGS = models.Keg.objects.all()
ALL_METERS = models.FlowMeter.objects.all()


class ChangeKegForm(forms.Form):
    keg_size = forms.ChoiceField(choices=keg_sizes.CHOICES,
        initial=keg_sizes.HALF_BARREL,
        required=True)


    initial_volume = forms.FloatField(label='Initial Volume (Liters)', initial=0.0, 
        required=False, help_text='Keg\'s Initial Volume in Liters')

    beer_name = forms.CharField(required=False)  # legacy
    brewer_name = forms.CharField(required=False)  # legacy

    beverage_name = forms.CharField(label='Beer Name', required=False)
    beverage_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    producer_name = forms.CharField(label='Brewer', required=False)
    producer_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    style_name = forms.CharField(required=True, label='Style',
      help_text='Example: Pale Ale, Stout, etc.')

    helper = FormHelper()
    helper.form_class = 'form-horizontal beer-select'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'beverage_name',
        Field('beverage_id', type='hidden'),
        'producer_name',
        Field('producer_id', type='hidden'),
        'style_name',
        'keg_size',
        'initial_volume',
        FormActions(
            Submit('submit_change_keg_form', 'Activate Keg', css_class='btn-primary'),
        )
    )

    def clean_beverage_name(self):
        beverage_name = self.cleaned_data.get('beverage_name')
        if not beverage_name:
            beverage_name = self.cleaned_data.get('beer_name')
            if not beverage_name:
                raise forms.ValidationError('Must specify a beverage name')
            self.cleaned_data['beverage_name'] = beverage_name
        return beverage_name

    def clean_producer_name(self):
        producer_name = self.cleaned_data.get('producer_name')
        if not producer_name:
            producer_name = self.cleaned_data.get('brewer_name')
            if not producer_name:
                raise forms.ValidationError('Must specify a producer name')
            self.cleaned_data['producer_name'] = producer_name
        return producer_name

    def save(self, tap):
        if not self.is_valid():
            raise ValueError('Form is not valid.')
        b = backend.KegbotBackend()

        if tap.is_active():
            b.end_keg(tap)

        keg_size = self.cleaned_data.get('keg_size')
        full_volume_ml = self.cleaned_data.get('full_volume_ml')
        
        if keg_size != 'other':
            full_volume_ml = None
        else:
            initial_volume = self.cleaned_data.get('initial_volume')
            full_volume_ml = float(units.Quantity(initial_volume, units.UNITS.Liter).InMilliliters())

        # TODO(mikey): Support non-beer beverage types.
        cd = self.cleaned_data
        keg = b.start_keg(tap, beverage_name=cd['beverage_name'], producer_name=cd['producer_name'],
            beverage_type='beer', style_name=cd['style_name'], keg_type=cd['keg_size'], 
            full_volume_ml=full_volume_ml)

        if cd.get('description'):
            keg.description = cd['description']
            keg.save()


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
    class FlowMeterModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, meter):
            if meter.tap:
                return '%s (connected to %s)' % (meter, meter.tap.name)
            else:
                return str(meter)

    meter = FlowMeterModelChoiceField(queryset=ALL_METERS, required=False,
        empty_label='Not connected.',
        help_text='Currently-assigned flow meter.')

    class Meta:
        model = models.KegTap
        fields = ('name', 'relay_name', 'description', 'temperature_sensor')

    def __init__(self, *args, **kwargs):
        super(TapForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['meter'].initial = self.instance.current_meter()

        self.fields['temperature_sensor'].queryset = models.ThermoSensor.objects.all()
        self.fields['temperature_sensor'].empty_label = 'No sensor.'

    def save(self, commit=True):
        if not commit:
            raise ValueError('TapForm does not support commit=False')
        instance = super(TapForm, self).save(commit=True)

        old_meter = instance.current_meter()
        new_meter = self.cleaned_data['meter']

        if old_meter != new_meter:
            if old_meter:
                old_meter.tap = None
                old_meter.save()
            if new_meter:
                new_meter.tap = instance
                new_meter.save()
        return instance

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'name',
        'meter',
        'relay_name',
        'temperature_sensor',
        'description',
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

class KegForm(forms.Form):
    keg_size = forms.ChoiceField(choices=keg_sizes.CHOICES,
        initial=keg_sizes.HALF_BARREL,
        required=True)

    initial_volume = forms.FloatField(label='Initial Volume (Liters)', initial=0.0, 
        required=False, help_text='Keg\'s Initial Volume in Liters')

    beer_name = forms.CharField(required=False)  # legacy
    brewer_name = forms.CharField(required=False)  # legacy

    beverage_name = forms.CharField(label='Beer Name', required=False)
    beverage_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    producer_name = forms.CharField(label='Brewer', required=False)
    producer_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    style_name = forms.CharField(required=True, label='Style',
      help_text='Example: Pale Ale, Stout, etc.')

    description = forms.CharField(max_length=256, label='Description', 
        widget=forms.Textarea(), required=False, 
        help_text='User-visible description of the Keg.')
    notes = forms.CharField(label='Notes', required=False, widget=forms.Textarea(),
        help_text='Private notes about this keg, viewable only by admins.')

    helper = FormHelper()
    helper.form_class = 'form-horizontal beer-select'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'beverage_name',
        Field('beverage_id', type='hidden'),
        'producer_name',
        Field('producer_id', type='hidden'),
        'style_name',
        'keg_size',
        'initial_volume',
        'description',
        'notes',
        FormActions(
            Submit('submit_add_keg', 'Save', css_class='btn-primary'),
        )
    )

    def clean_beverage_name(self):
        beverage_name = self.cleaned_data.get('beverage_name')
        if not beverage_name:
            beverage_name = self.cleaned_data.get('beer_name')
            if not beverage_name:
                raise forms.ValidationError('Must specify a beverage name')
            self.cleaned_data['beverage_name'] = beverage_name
        return beverage_name

    def clean_producer_name(self):
        producer_name = self.cleaned_data.get('producer_name')
        if not producer_name:
            producer_name = self.cleaned_data.get('brewer_name')
            if not producer_name:
                raise forms.ValidationError('Must specify a producer name')
            self.cleaned_data['producer_name'] = producer_name
        return producer_name

    def save(self):
        if not self.is_valid():
            raise ValueError('Form is not valid.')
        b = backend.KegbotBackend()
        keg_size = self.cleaned_data.get('keg_size')
        notes = self.cleaned_data.get('notes')
        description = self.cleaned_data.get('description')
        if keg_size != 'other':
            full_volume_ml = None
        else:
            initial_volume = self.cleaned_data.get('initial_volume')
            full_volume_ml = float(units.Quantity(initial_volume, units.UNITS.Liter).InMilliliters())

        # TODO(mikey): Support non-beer beverage types.
        cd = self.cleaned_data
        keg = b.add_keg(beverage_name=cd['beverage_name'], producer_name=cd['producer_name'],
            beverage_type='beer', style_name=cd['style_name'], keg_type=cd['keg_size'], 
            full_volume_ml=full_volume_ml, notes=cd['notes'], description=cd['description'])
        return keg


class EditKegForm(forms.ModelForm):
    class Meta:
        model = models.Keg
        fields = ('spilled_ml', 'description', 'notes',)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'spilled_ml',
        'description',
        'notes',
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )


class SiteSettingsForm(forms.ModelForm):
    guest_image = forms.ImageField(required=False,
        help_text='Custom image for the "guest" user.')

    class Meta:
        model = models.SiteSettings
        fields = (
            'title',
            'privacy',
            'volume_display_units',
            'temperature_display_units',
            'timezone',
            'hostname',
            'use_ssl',
            'session_timeout_minutes',
            'google_analytics_id',
            'guest_name',
            'default_user',
            'registration_allowed',
            'registration_confirmation',
            'check_for_updates',
            'allowed_hosts',
        )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'title',
        'privacy',
        'volume_display_units',
        'temperature_display_units',
        'timezone',
        'hostname',
        'use_ssl',
        'session_timeout_minutes',
        'google_analytics_id',
        'guest_name',
        'guest_image',
        'default_user',
        'registration_allowed',
        'registration_confirmation',
        'check_for_updates',
        'allowed_hosts',
        FormActions(
            Submit('submit', 'Save Settings', css_class='btn-primary'),
        )
    )

class BeverageForm(forms.ModelForm):
    class Meta:
        model = models.Beverage
        fields = ('name', 'style', 'producer', 'vintage_year', 'abv_percent',
            'original_gravity', 'specific_gravity',
            'untappd_beer_id')

    new_image = forms.ImageField(required=False,
        help_text='Set/replace image for this beer type.')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'name',
        'style',
        'producer',
        'vintage_year',
        'abv_percent',
        'original_gravity',
        'specific_gravity',
        'untappd_beer_id',
        'new_image',
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )

class BeverageProducerForm(forms.ModelForm):
    class Meta:
        model = models.BeverageProducer

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'name',
        'country',
        'origin_state',
        'origin_city',
        'is_homebrew',
        'url',
        'description',
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )

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
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'username',
        'email',
        'password',
        'is_staff',
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )

class EditUserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = (
            'email',
        )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('email', css_class='input-xlarge'),
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )

class TokenForm(forms.ModelForm):
    class Meta:
        model = models.AuthenticationToken
        fields = (
            'nice_name',
            'enabled',
        )
    username = forms.CharField(required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal user-select'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'username',
        'nice_name'
        'enabled',
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if username == '':
            self.cleaned_data['user'] = None
            return
        try:
            self.cleaned_data['user'] = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            raise forms.ValidationError('Invalid username; use a complete user name or leave blank.')
        return username


class AddTokenForm(forms.ModelForm):
    class Meta:
        model = models.AuthenticationToken
        fields = (
            'auth_device',
            'token_value',
            'enabled',
        )
    CHOICES = (
      ('core.rfid', 'RFID'),
      ('core.onewire', 'OneWire/iButton'),
      ('nfc', 'NFC'),
    )
    auth_device = forms.ChoiceField(choices=CHOICES)
    username = forms.CharField(required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal user-select'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-6'
    helper.layout = Layout(
        'auth_device',
        'token_value',
        'username',
        'enabled',
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if username == '':
            self.cleaned_data['user'] = None
            return
        try:
            self.cleaned_data['user'] = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            raise forms.ValidationError('Invalid username; use a complete user name or leave blank.')
        return username


class CancelDrinkForm(forms.Form):
    pass

class ReassignDrinkForm(forms.Form):
    username = forms.CharField(required=False)

class ChangeDrinkVolumeForm(forms.Form):
    UNIT_CHOICES = (
      ('mL', 'mL'),
      ('oz', 'oz')
    )
    units = forms.ChoiceField(required=True, choices=UNIT_CHOICES)
    volume = forms.FloatField(required=True, min_value=0)

    def clean_volume(self):
        volume = self.cleaned_data['volume']
        if self.cleaned_data['units'] == 'oz':
            self.cleaned_data['volume_ml'] = float(units.Quantity(volume, units.UNITS.Ounce).InMilliliters())
        else:
            self.cleaned_data['volume_ml'] = volume
        return volume

class RecordDrinkForm(forms.Form):
    units = forms.ChoiceField(required=True, choices=ChangeDrinkVolumeForm.UNIT_CHOICES)
    volume = forms.FloatField(required=True, min_value=0)
    username = forms.CharField(required=False)

    def clean_username(self):
        username = self.cleaned_data['username']
        if username == '':
            self.cleaned_data['user'] = None
            return
        try:
            self.cleaned_data['user'] = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            raise forms.ValidationError('Invalid username; use a complete user name or leave blank.')
        return username

    def clean_volume(self):
        volume = self.cleaned_data['volume']
        if self.cleaned_data['units'] == 'oz':
            self.cleaned_data['volume_ml'] = float(units.Quantity(volume, units.UNITS.Ounce).InMilliliters())
        else:
            self.cleaned_data['volume_ml'] = volume
        return volume


class FlowMeterForm(forms.ModelForm):
    class Meta:
        model = models.FlowMeter
        fields = ('port_name', 'ticks_per_ml')


class DeleteControllerForm(forms.Form):
    helper = FormHelper()
    helper.form_class = 'form-horizontal user-select'
    helper.layout = Layout(
        FormActions(
            Submit('delete', 'Delete Controller', css_class='btn-primary'),
        )
    )


class ControllerForm(forms.ModelForm):
    class Meta:
        model = models.Controller
        fields = ('name', 'model_name', 'serial_number')
