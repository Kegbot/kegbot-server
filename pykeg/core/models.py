# -*- coding: latin-1 -*-
# Copyright 2008 Mike Wakerly <opensource@hoho.com>
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
from django.contrib.auth.models import User
from django.contrib import admin

from pykeg.core import kb_common
from pykeg.core import units
from pykeg.core import util

SCHEMA_VERSION = 21

# This is a Django models definition for the kegbot database

class UserPicture(models.Model):
  def __str__(self):
    return "%s UserPicture" % (self.user,)

  user = models.OneToOneField(User)
  image = models.ImageField(upload_to='mugshots')
  active = models.BooleanField(default=True)

admin.site.register(UserPicture)


class UserLabel(models.Model):
  labelname = models.CharField(max_length=128)

  def __str__(self):
    return str(self.labelname)

admin.site.register(UserLabel)


class UserProfile(models.Model):
  """Extra per-User information."""
  def __str__(self):
    return "profile for %s" % (self.user,)

  def HasLabel(self, lbl):
    for l in self.labels.all():
      if l.labelname == lbl:
        return True
    return False

  user = models.OneToOneField(User)
  gender = models.CharField(max_length=8)
  weight = models.FloatField()
  labels = models.ManyToManyField(UserLabel)

admin.site.register(UserProfile)


class Brewer(models.Model):
  name = models.CharField(max_length=128)
  origin_country = models.CharField(max_length=128, default='')
  origin_state = models.CharField(max_length=128, default='')
  origin_city = models.CharField(max_length=128, default='')
  distribution = models.CharField(max_length=128,
      choices = ( ('retail', 'retail'),
                  ('homebrew', 'homebrew'),
                  ('unknown', 'unknown'),
      ),
      default = 'unknown',
  )
  url = models.URLField(verify_exists=False, default='')
  comment = models.TextField(default='')

  def __str__(self):
    return "%s (%s, %s, %s)" % (self.name, self.origin_city,
                                self.origin_state, self.origin_country)

admin.site.register(Brewer)


class BeerStyle(models.Model):
  name = models.CharField(max_length=128)

  def __str__(self):
    return self.name

admin.site.register(BeerStyle)


class BeerType(models.Model):
  """ Record to link a beverage to its brewer and composition.

  Each installed Keg must be assigned a BeerType so that various intake
  estimates (BAC, calories, and so on) can be made.
  """
  name = models.CharField(max_length=128)
  brewer = models.ForeignKey(Brewer)
  style = models.ForeignKey(BeerStyle)
  calories_oz = models.FloatField(default=0)
  carbs_oz = models.FloatField(default=0)
  abv = models.FloatField(default=0)

  def __str__(self):
    return "%s by %s" % (self.name, self.brewer)


class BeerTypeAdmin(admin.ModelAdmin):
  list_display = ('name', 'brewer', 'style')

admin.site.register(BeerType, BeerTypeAdmin)


class KegSize(models.Model):
  """ A convenient table of common Keg sizes """
  def Volume(self):
    return units.Quantity(self.volume, units.RECORD_UNIT)

  def __str__(self):
    return "%s (%i ounces)" % (self.name, self.Volume().ConvertTo.Ounce)

  name = models.CharField(max_length=128)
  volume = models.IntegerField()

admin.site.register(KegSize)


class Keg(models.Model):
  """ Record for each installed Keg. """
  def full_volume(self):
    return self.size.volume

  def served_volume(self):
    drinks = Drink.objects.filter(keg__exact=self, status__exact='valid')
    tot = 0.0
    for d in drinks:
      tot += d.volume
    return tot

  def remaining_volume(self):
    return self.full_volume() - self.served_volume()

  def __str__(self):
    return "Keg #%s - %s" % (self.id, self.type)

  type = models.ForeignKey(BeerType)
  size = models.ForeignKey(KegSize)
  startdate = models.DateTimeField('start date', default=datetime.datetime.now)
  enddate = models.DateTimeField('end date', default=datetime.datetime.now)
  channel = models.IntegerField()
  status = models.CharField(max_length=128, choices=(
     ('online', 'online'),
     ('offline', 'offline'),
     ('coming soon', 'coming soon')))
  description = models.CharField(max_length=256)
  origcost = models.FloatField(default=0)

class KegAdmin(admin.ModelAdmin):
  list_display = ('id', 'type')

admin.site.register(Keg, KegAdmin)


class Drink(models.Model):
  """ Table of drinks records """
  class Meta:
    get_latest_by = "starttime"

  def Volume(self):
    return units.Quantity(self.volume, units.RECORD_UNIT)

  def calories(self):
    cal = self.keg.type.calories_oz * self.Volume().ConvertTo.Ounce
    return cal

  def bac(self):
    bacs = BAC.objects.filter(drink__exact=self)
    if bacs.count() == 1:
      return bacs[0].bac
    return 0

  def __str__(self):
    return "Drink %s by %s" % (self.id, self.user)

  # Ticks and volume may seem redundant; volume is stored in "volunits" which
  # happen to be the exact volume of one tick. The idea here is to always
  # store the meter reading, in case the value of a volunit changes, and to
  # allow calibration. Kegbot code never touches the ticks field after saving
  # it; all operations concerning volume use the volume field.
  ticks = models.PositiveIntegerField()
  volume = models.PositiveIntegerField()

  # Similarly, recording both the start and end times of a drink may seem odd.
  # The idea was to someday add metrics to the web page showing pour speeds.
  # This was never terribly exciting so it didn't happen, but space is cheap
  # so I'm inclined to keep the data rather than chuck it.
  #
  # For sorting and other operations requiring a single date, the endtime is
  # used.  TODO(mikey): make sure this is actually the case
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()
  user = models.ForeignKey(User)
  keg = models.ForeignKey(Keg, null=True, blank=True)
  status = models.CharField(max_length=128, choices = (
     ('valid', 'valid'),
     ('invalid', 'invalid'),
     ), default = 'valid')

admin.site.register(Drink)


class Token(models.Model):
  """ An arbitrary secret key, used by the authentication system.

  This table may need to change as more authentication modules are added.
  TODO(mikey): fix this
  """
  def __str__(self):
    return "Token %s for %s" % (self.id, self.user)

  user = models.ForeignKey(User)
  keyinfo = models.TextField()
  created = models.DateTimeField(default=datetime.datetime.now)

admin.site.register(Token)


class BAC(models.Model):
  """ Calculated table of instantaneous blood alcohol estimations.

  A BAC value may be added by Kegbot after each pour of a registered drinker.
  A relationship to the drink causing the calculation is stored, to ease
  lookup by Drink.

  TODO(mikey): consider making the Drink optional so that intermediate values
  can be added. Seems of dubious utility.
  TODO(mikey): if Drink is mandatory, should eliminated rectime.
  """
  user = models.ForeignKey(User)
  drink = models.ForeignKey(Drink)
  rectime = models.DateTimeField()
  bac = models.FloatField()

  def __str__(self):
    return "%s BAC at %s" % (self.user, self.drink)

  @classmethod
  def ProcessDrink(cls, d):
    """Generate the bac for a drink"""
    try:
      profile = d.user.get_profile()
    except UserProfile.DoesNotExist:
      # can't compute bac if there is no profile
      return
    if profile.HasLabel('__no_bac__'):
      return

    # TODO: delete/update previous bac for this drink iff exists

    # consider previously recorded bac for non-guest users
    matches = BAC.objects.filter(user=d.user).order_by('-rectime')
    prev_bac = 0
    if len(matches):
      last_bac = matches[0]
      prev_bac = util.decomposeBAC(last_bac.bac, (d.endtime - last_bac.rectime).seconds)

    now = util.instantBAC(profile.gender, profile.weight, d.keg.type.abv,
                          d.Volume().ConvertTo.Ounce)
    b = BAC(user=d.user, drink=d, rectime=d.endtime, bac=now+prev_bac)
    b.save()

admin.site.register(BAC)


class Binge(models.Model):
  """ A calculated grouping of drinks occuring within a time window """
  def __str__(self):
    return "binge %s by %s (%s to %s)" % (self.id, self.user, self.starttime, self.endtime)

  user = models.ForeignKey(User)
  startdrink = models.ForeignKey(Drink, related_name='start')
  enddrink = models.ForeignKey(Drink, related_name='end')
  volume = models.PositiveIntegerField()
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()

  @classmethod
  def Assign(cls, d):
    """ Create or update a binge given a recent drink """
    try:
      profile = d.user.get_profile()
      if profile.HasLabel('__no_binge__'):
        return
    except UserProfile.DoesNotExist:
      pass

    binge_window = datetime.timedelta(minutes=kb_common.BINGE_TIME_MINUTES)
    min_end = d.endtime - binge_window
    binges = Binge.objects.filter(user=d.user, starttime__lte=d.starttime,
                                  endtime__gte=min_end).order_by("-id")[:1]

    # now find or create the current binge, and update it
    if not len(binges):
      new_binge = Binge(user=d.user, startdrink=d,
                        enddrink=d, volume=d.Volume().Amount(units.RECORD_UNIT),
                        starttime=d.endtime,
                        endtime=d.endtime + binge_window)
      new_binge.save()
      return
    else:
      last_binge = binges[0]
      last_binge.volume += d.volume
      last_binge.enddrink = d
      last_binge.endtime = d.endtime + binge_window
      last_binge.save()

admin.site.register(Binge)


class Thermolog(models.Model):
  """ A log from an ITemperatureSensor device of periodic measurements. """
  name = models.CharField(max_length=128)
  temp = models.FloatField()
  time = models.DateTimeField()

admin.site.register(Thermolog)


class RelayLog(models.Model):
  """ A log from an IRelay device of relat events/ """
  name = models.CharField(max_length=128)
  status = models.CharField(max_length=32)
  time = models.DateTimeField()

admin.site.register(RelayLog)


class Config(models.Model):
  def __str__(self):
    return '%s=%s' % (self.key, self.value)

  key = models.CharField(max_length=128)
  value = models.TextField()

admin.site.register(Config)
