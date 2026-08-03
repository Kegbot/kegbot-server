from django import forms

from pykeg.core import models
from pykeg.core.kb_common import USERNAME_REGEX


class DrinkPostForm(forms.Form):
    """Form to handle posts to /tap/<tap_id>/"""

    ticks = forms.IntegerField()
    volume_ml = forms.FloatField(required=False)
    username = forms.RegexField(required=False, max_length=30, regex=USERNAME_REGEX)
    record_date = forms.CharField(required=False)
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


class TapCreateForm(forms.Form):
    name = forms.CharField()


class ControllerForm(forms.ModelForm):
    """Relocated from the old kegadmin app; used by legacy POSTs."""

    class Meta:
        model = models.Controller
        fields = ("name", "model_name", "serial_number")


class NewFlowMeterForm(forms.ModelForm):
    """Relocated from the old kegadmin app; used by legacy POSTs."""

    class Meta:
        model = models.FlowMeter
        fields = ("port_name", "ticks_per_ml", "controller")
