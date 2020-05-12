from builtins import object
from django import forms

from pykeg.core import models
from pykeg.core.kb_common import USERNAME_REGEX

ALL_METERS = models.FlowMeter.objects.all()
ALL_TOGGLES = models.FlowToggle.objects.all()
ALL_THERMOS = models.ThermoSensor.objects.all()


class DrinkPostForm(forms.Form):
    """Form to handle posts to /tap/<tap_id>/"""

    ticks = forms.IntegerField()
    volume_ml = forms.FloatField(required=False)
    username = forms.RegexField(required=False, max_length=30, regex=USERNAME_REGEX)
    pour_time = forms.IntegerField(required=False)
    now = forms.IntegerField(required=False)
    duration = forms.IntegerField(required=False)
    shout = forms.CharField(required=False)
    tick_time_series = forms.CharField(required=False)


class CancelDrinkForm(forms.Form):
    """Form to handled posts to /cancel-drink/"""

    id = forms.IntegerField()
    spilled = forms.BooleanField(required=False)


class ThermoPostForm(forms.Form):
    """Handles posting new temperature sensor readings."""

    temp_c = forms.FloatField()
    when = forms.IntegerField(required=False)
    now = forms.IntegerField(required=False)


class CreateKegTapForm(forms.ModelForm):
    class Meta(object):
        model = models.KegTap
        fields = ("name", "notes")


class CalibrateTapForm(forms.Form):
    ml_per_tick = forms.FloatField()


class TapCreateForm(forms.Form):
    name = forms.CharField()


class TapSpillForm(forms.Form):
    volume_ml = forms.FloatField()


class DebugLogForm(forms.Form):
    message = forms.CharField()
    client_name = forms.CharField(required=False)


class RegisterForm(forms.Form):
    username = forms.RegexField(max_length=30, regex=r"^[\w-]+$")
    email = forms.EmailField()
    password = forms.CharField(required=False)
    photo = forms.ImageField(required=False)


class AssignTokenForm(forms.Form):
    username = forms.RegexField(max_length=30, regex=r"^[\w-]+$")


class ConnectMeterForm(forms.Form):
    meter = forms.ModelChoiceField(queryset=ALL_METERS, required=True)


class ConnectToggleForm(forms.Form):
    toggle = forms.ModelChoiceField(queryset=ALL_TOGGLES, required=True)


class ConnectThermoForm(forms.Form):
    thermo = forms.ModelChoiceField(queryset=ALL_THERMOS, required=True)
