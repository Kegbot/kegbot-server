from django import forms
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Field
from crispy_forms.bootstrap import FormActions

from kegbot.util import units
from pykeg.backend import get_kegbot_backend
from pykeg.core import keg_sizes
from pykeg.core import models

ALL_TAPS = models.KegTap.objects.all()
ALL_KEGS = models.Keg.objects.all()
ALL_METERS = models.FlowMeter.objects.all()
ALL_TOGGLES = models.FlowToggle.objects.all()
ALL_THERMOS = models.ThermoSensor.objects.all()


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
    helper.layout = Layout(
        Field('beverage_name', css_class='input-xlarge'),
        Field('beverage_id', type='hidden'),
        Field('producer_name', css_class='input-xlarge'),
        Field('producer_id', type='hidden'),
        Field('style_name', css_class='input-xlarge'),
        Field('keg_size', css_class='input-xlarge'),
        Div(
            Field('initial_volume', css_class='input-volume', type='hidden'),
            css_class="variable-units"),
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
        b = get_kegbot_backend()

        if tap.is_active():
            b.end_keg(tap)

        keg_size = self.cleaned_data.get('keg_size')
        full_volume_ml = self.cleaned_data.get('full_volume_ml')

        if keg_size != 'other':
            full_volume_ml = None
        else:
            full_volume_ml = self.cleaned_data.get('initial_volume')

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
                return u'{} (connected to {})'.format(meter, meter.tap.name)
            else:
                return unicode(meter)

    class FlowToggleModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, toggle):
            if toggle.tap:
                return u'{} (connected to {})'.format(toggle, toggle.tap.name)
            else:
                return unicode(toggle)

    class ThermoSensorModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, sensor):
            last_log = sensor.LastLog()
            if last_log:
                return u'{} (Last report: {})'.format(sensor, naturaltime(last_log.time))
            else:
                return unicode(sensor)

    meter = FlowMeterModelChoiceField(queryset=ALL_METERS, required=False,
        empty_label='Not connected.',
        help_text='Tap is routed thorough this flow meter. If unset, reporting is disabled.')

    toggle = FlowToggleModelChoiceField(queryset=ALL_TOGGLES, required=False,
        empty_label='Not connected.',
        help_text='Optional flow toggle (usually a relay/valve) connected to this tap.')

    temperature_sensor = ThermoSensorModelChoiceField(queryset=ALL_THERMOS, required=False,
        empty_label='No sensor.',
        help_text='Optional sensor monitoring the temperature at this tap.')

    class Meta:
        model = models.KegTap
        fields = ('name', 'description', 'temperature_sensor', 'sort_order')

    def __init__(self, *args, **kwargs):
        super(TapForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['meter'].initial = self.instance.current_meter()
            self.fields['toggle'].initial = self.instance.current_toggle()
            self.fields['temperature_sensor'].initial = self.instance.temperature_sensor

    def save(self, commit=True):
        if not commit:
            raise ValueError('TapForm does not support commit=False')
        instance = super(TapForm, self).save(commit=True)
        b = get_kegbot_backend()
        b.connect_meter(instance, self.cleaned_data['meter'])
        b.connect_toggle(instance, self.cleaned_data['toggle'])
        return instance

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('name', css_class='input-xlarge'),
        Field('meter', css_class='input-xlarge'),
        Field('toggle', css_class='input-xlarge'),
        Field('temperature_sensor', css_class='input-xlarge'),
        Field('sort_order', css_class='input-xlarge'),
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
    helper.layout = Layout(
        Field('beverage_name', css_class='input-xlarge'),
        Field('beverage_id', type='hidden'),
        Field('producer_name', css_class='input-xlarge'),
        Field('producer_id', type='hidden'),
        Field('style_name', css_class='input-xlarge'),
        Field('keg_size', css_class='input-xlarge'),
        Div(
            Field('initial_volume', css_class='input-volume', type='hidden'),
            css_class='variable-units'),
        Field('description'),
        Field('notes'),
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
        keg_size = self.cleaned_data.get('keg_size')
        if keg_size != 'other':
            full_volume_ml = None
        else:
            full_volume_ml = self.cleaned_data.get('initial_volume')

        # TODO(mikey): Support non-beer beverage types.
        cd = self.cleaned_data
        b = get_kegbot_backend()
        keg = b.create_keg(beverage_name=cd['beverage_name'], producer_name=cd['producer_name'],
            beverage_type='beer', style_name=cd['style_name'], keg_type=cd['keg_size'],
            full_volume_ml=full_volume_ml, notes=cd['notes'], description=cd['description'])
        return keg


class EditKegForm(forms.ModelForm):
    class Meta:
        model = models.Keg
        fields = ('spilled_ml', 'description', 'notes',)
        labels = {
            'spilled_ml': ('Spilled Volume'),
        }

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Div(
            Field('spilled_ml', css_class='input-volume', type='hidden'),
            css_class="variable-units"),
        Field('description'),
        Field('notes'),
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )


class GeneralSiteSettingsForm(forms.ModelForm):
    class Meta:
        model = models.KegbotSite
        fields = (
            'title',
            'privacy',
            'registration_mode',
        )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('title', css_class='input-xlarge'),
        Field('privacy', css_class='input-xlarge'),
        Field('registration_mode', css_class='input-xlarge'),
        FormActions(
            Submit('submit', 'Save Settings', css_class='btn-primary'),
        )
    )


class LocationSiteSettingsForm(forms.ModelForm):
    guest_image = forms.ImageField(required=False,
        help_text='Custom image for the "guest" user.')

    class Meta:
        model = models.KegbotSite
        fields = (
            'volume_display_units',
            'temperature_display_units',
            'timezone',
        )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('volume_display_units', css_class='input-xlarge'),
        Field('temperature_display_units', css_class='input-xlarge'),
        Field('timezone'),
        FormActions(
            Submit('submit', 'Save Settings', css_class='btn-primary'),
        )
    )


class AdvancedSiteSettingsForm(forms.ModelForm):
    class Meta:
        model = models.KegbotSite
        fields = (
            'session_timeout_minutes',
            'google_analytics_id',
            'check_for_updates',
        )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('session_timeout_minutes'),
        Field('google_analytics_id'),
        Field('check_for_updates'),
        FormActions(
            Submit('submit', 'Save Settings', css_class='btn-primary'),
        )
    )


class BeverageForm(forms.ModelForm):
    class Meta:
        model = models.Beverage
        fields = ('name', 'style', 'producer', 'vintage_year', 'abv_percent',
            'original_gravity', 'specific_gravity',
            'untappd_beer_id', 'description')

    new_image = forms.ImageField(required=False,
        help_text='Set/replace image for this beer type.')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('name', css_class='input-xlarge'),
        Field('style', css_class='input-xlarge'),
        Field('producer'),
        Field('vintage_year'),
        Field('abv_percent'),
        Field('original_gravity'),
        Field('specific_gravity'),
        Field('untappd_beer_id'),
        Field('description'),
        Field('new_image'),
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )


class BeverageProducerForm(forms.ModelForm):
    class Meta:
        model = models.BeverageProducer

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('name', css_class='input-xlarge'),
        Field('country', css_class='input-xlarge'),
        Field('origin_state', css_class='input-xlarge'),
        Field('origin_city', css_class='input-xlarge'),
        Field('is_homebrew'),
        Field('url'),
        Field('description'),
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
    helper.layout = Layout(
        Field('username', css_class='input-xlarge'),
        Field('email', css_class='input-xlarge'),
        'password',
        'is_staff',
        FormActions(
            Submit('submit', 'Save', css_class='btn-primary'),
        )
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('display_name',)
        if settings.EMBEDDED:
            fields = ('email', ) + fields

    new_mugshot = forms.ImageField(required=False)

    def save(self, *args, **kwargs):
        user = super(UserProfileForm, self).save(*args, **kwargs)
        image = self.cleaned_data.get('new_mugshot')
        if image:
            pic = models.Picture.objects.create(user=user)
            pic.image.save(image.name, image)
            pic.save()
            user.mugshot = pic
            user.save()
        return user


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
    helper.layout = Layout(
        Field('username', css_class='input-xlarge'),
        Field('nice_name', css_class='input-xlarge'),
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
    helper.layout = Layout(
        Field('auth_device', css_class='input-xlarge'),
        Field('token_value', css_class='input-xlarge'),
        Field('username', css_class='input-xlarge'),
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
    username = forms.CharField(required=True)


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


class TestEmailForm(forms.Form):
    address = forms.CharField(required=False)

    def clean_address(self):
        address = self.cleaned_data['address']
        if address == '':
            self.cleaned_data['address'] = None
            return
        return address


class NewFlowMeterForm(forms.ModelForm):
    class Meta:
        model = models.FlowMeter
        fields = ('port_name', 'ticks_per_ml', 'controller')


class UpdateFlowMeterForm(forms.ModelForm):
    class Meta:
        model = models.FlowMeter
        fields = ('ticks_per_ml',)


class AddFlowMeterForm(forms.ModelForm):
    class Meta:
        model = models.FlowMeter
        fields = ('port_name', 'ticks_per_ml', 'controller')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('port_name'),
        Field('ticks_per_ml'),
        Field('controller', type='hidden'),
        FormActions(
            Submit('add_flow_meter', 'Add Flow Meter', css_class='btn-primary'),
        )
    )


class FlowToggleForm(forms.ModelForm):
    class Meta:
        model = models.FlowToggle
        fields = ('port_name', 'controller')


class AddFlowToggleForm(forms.ModelForm):
    class Meta:
        model = models.FlowToggle
        fields = ('port_name', 'controller')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('port_name'),
        Field('controller', type='hidden'),
        FormActions(
            Submit('add_flow_toggle', 'Add Flow Toggle', css_class='btn-primary'),
        )
    )


class DeleteControllerForm(forms.Form):
    helper = FormHelper()
    helper.form_class = 'form-horizontal user-select'
    helper.layout = Layout(
        FormActions(
            Submit('delete_controller', 'Delete Controller', css_class='btn-danger'),
        )
    )


class ControllerForm(forms.ModelForm):
    class Meta:
        model = models.Controller
        fields = ('name', 'model_name', 'serial_number')


class LinkDeviceForm(forms.Form):
    code = forms.CharField(required=True,
        help_text='Link code shown on device.')
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        'code',
        FormActions(
            Submit('link_device', 'Link Device', css_class='btn-success'),
        )
    )
