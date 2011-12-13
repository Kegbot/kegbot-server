from django import forms

from pykeg.core import models
from pykeg.beerdb import models as bdb

ALL_TAPS = models.KegTap.objects.all()
ALL_SIZES = models.KegSize.objects.all()
ALL_BEER_TYPES = bdb.BeerType.objects.all().order_by('name')
ALL_KEGS = models.Keg.objects.all()

class GeneralSettingsForm(forms.Form):
  name = forms.CharField(help_text='Name of this Kegbot system')

class ChangeKegForm(forms.Form):
  keg_size = forms.ModelChoiceField(queryset=ALL_SIZES,
      empty_label=None,
      help_text='Size of the new keg')

  beer_type = forms.ModelChoiceField(queryset=ALL_BEER_TYPES,
      empty_label=None,
      help_text='Choose existing type')

  cost = forms.FloatField(required=False, min_value=0,
      help_text='Price paid (optional)')
  description = forms.CharField(required=False,
      help_text='Public description of this specific keg (optional)')

class TapForm(forms.ModelForm):
  class Meta:
    model = models.KegTap

class KegHiddenSelectForm(forms.Form):
  keg = forms.ModelChoiceField(queryset=ALL_KEGS, widget=forms.HiddenInput)

class CreateTapForm(forms.ModelForm):
  class Meta:
    model = models.KegTap
    fields = ('name', 'meter_name', 'relay_name', 'ml_per_tick', 'description',
        'temperature_sensor')

class SiteSettingsForm(forms.ModelForm):
  class Meta:
    model = models.SiteSettings
    fields = ('title', 'description', 'display_units')

#BeerTypeFormSet = inlineformset_factory(models.Brewer, models.BeerType)
