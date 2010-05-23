# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

import datetime

from django.db import models
from pykeg.core import fields as core_fields
from django_extensions.db import fields as ext_fields

PRODUCTION_CHOICES = (
  ('commercial', 'Commercial brewer'),
  ('homebrew', 'Home brewer'),
)

class BeerDBModel(models.Model):
  class Meta:
    abstract = True
  id = ext_fields.UUIDField(auto=True, primary_key=True)
  revision = models.IntegerField(default=0, editable=False)
  added = models.DateTimeField(default=datetime.datetime.now, editable=False)
  edited = models.DateTimeField(editable=False)

  def save(self, *args, **kwargs):
    self.revision += 1
    self.edited = datetime.datetime.now()
    super(BeerDBModel, self).save(*args, **kwargs)


class Brewer(BeerDBModel):
  """Describes a producer of beer."""
  name = models.CharField(max_length=255,
      help_text='Name of the brewer')
  country = core_fields.CountryField(default='USA',
      help_text='Country of origin')
  origin_state = models.CharField(max_length=128,
      default='', blank=True, null=True,
      help_text='State of origin, if applicable')
  origin_city = models.CharField(max_length=128, default='', blank=True,
      null=True,
      help_text='City of origin, if known')
  production = models.CharField(max_length=128, choices=PRODUCTION_CHOICES,
      default='commercial')
  url = models.URLField(verify_exists=False, default='', blank=True, null=True,
      help_text='Brewer\'s home page')
  description = models.TextField(default='', blank=True, null=True,
      help_text='A short description of the brewer')

  def __str__(self):
    return self.name


class BeerStyle(BeerDBModel):
  """Describes a named style of beer (Stout, IPA, etc)"""
  name = models.CharField(max_length=128,
      help_text='Name of the beer style')

  def __str__(self):
    return self.name


class BeerType(BeerDBModel):
  """Describes a specific kind of beer, by name, brewer, and style."""
  name = models.CharField(max_length=255)
  brewer = models.ForeignKey(Brewer)
  style = models.ForeignKey(BeerStyle)

  edition = models.CharField(max_length=255, blank=True, null=True,
      help_text='For seasonal or special edition beers, enter the '
          'year or other edition name')

  abv = models.FloatField(blank=True, null=True,
      help_text='Alcohol by volume, as percentage (0-100), if known')
  calories_oz = models.FloatField(blank=True, null=True,
      help_text='Calories per ounce of beer, if known')
  carbs_oz = models.FloatField(blank=True, null=True,
      help_text='Carbohydrates per ounce of beer, if known')

  original_gravity = models.FloatField(blank=True, null=True,
      help_text='Original gravity of the beer, if known')
  specific_gravity = models.FloatField(blank=True, null=True,
      help_text='Specific/final gravity of the beer, if known')

  def __str__(self):
    return "%s by %s" % (self.name, self.brewer)

