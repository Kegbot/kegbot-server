# Copyright 2009 Mike Wakerly <opensource@hoho.com>
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

import random

from django.db import models
from django.contrib.auth.models import User

from pykeg.core import models as core_models
from pykeg.core import units

class UserTwitterLink(models.Model):
  """Maps a user to a particular twitter account."""
  user_profile = models.OneToOneField(core_models.UserProfile, primary_key=True)
  twitter_name = models.CharField(max_length=256)
  validated = models.BooleanField(default=True)


class TweetLog(models.Model):
  twitter_id = models.CharField(max_length=256)
  tweet = models.CharField(max_length=256)


class DrinkTweetLog(models.Model):
  tweet_log = models.ForeignKey(TweetLog)
  drink = models.ForeignKey(core_models.Drink)


class DrinkClassification(models.Model):
  name = models.CharField(max_length=256)
  minimum_volume_ml = models.FloatField()

  def __str__(self):
    vol = units.Quantity(self.minimum_volume_ml, units.UNITS.Milliliter)
    oz = vol.ConvertTo.Ounce
    return '%s (%.1foz or more)' % (self.name, oz)

  @classmethod
  def GetClassForDrink(cls, drink):
    all_classes = list(cls.objects.all().order_by('minimum_volume_ml'))
    if not all_classes:
      return None

    best = all_classes[0]
    if drink.volume_ml < best.minimum_volume_ml:
      return None
    for drink_class in all_classes[1:]:
      if drink.volume_ml < drink_class.minimum_volume_ml:
        return best
      best = drink_class
    return best


class DrinkRemark(models.Model):
  drink_class = models.ForeignKey(DrinkClassification)
  remark = models.CharField(max_length=256)

  def  __str__(self):
    return "%s [%s]" % (self.remark, self.drink_class.name)

  @classmethod
  def GetRemarkForDrink(cls, drink):
    drink_class = DrinkClassification.GetClassForDrink(drink)
    if not drink_class:
      return None
    remarks = list(drink_class.drinkremark_set.all())
    if not remarks:
      return None
    return random.choice(remarks)
