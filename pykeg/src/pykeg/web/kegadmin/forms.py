from django import forms

from pykeg.core import models
from pykeg.beerdb import models as bdb

ALL_TAPS = models.KegTap.objects.all()
ALL_SIZES = models.KegSize.objects.all()
ALL_BEER_TYPES = bdb.BeerType.objects.all().order_by('name')

class GeneralSettingsForm(forms.Form):
  name = forms.CharField(help_text='Name of this Kegbot system')

class ChangeKegForm(forms.Form):
  tap = forms.ModelChoiceField(queryset=ALL_TAPS,
      empty_label=None,
      help_text='Select tap to add/replace keg')

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

#BeerTypeFormSet = inlineformset_factory(models.Brewer, models.BeerType)
