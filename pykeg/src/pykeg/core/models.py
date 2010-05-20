# -*- coding: latin-1 -*-
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
import os
import random

from django.conf import settings
from django.core import urlresolvers
from django.db import models
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from pykeg.core import kb_common
from pykeg.core import fields
from pykeg.core import stats
from pykeg.core import units
from pykeg.core import util

from pykeg.beerdb import models as bdb

from django_extensions.db.fields.json import JSONField

"""Django models definition for the kegbot database."""

def mugshot_file_name(instance, filename):
  rand_salt = random.randrange(0xffff)
  new_filename = '%04x-%s' % (rand_salt, filename)
  return os.path.join('mugshots', instance.user.username, new_filename)


class UserPicture(models.Model):
  def __str__(self):
    return "%s UserPicture" % (self.user,)

  user = models.ForeignKey(User)
  image = models.ImageField(upload_to=mugshot_file_name)
  active = models.BooleanField(default=True)


class UserLabel(models.Model):
  labelname = models.CharField(max_length=128)

  def __str__(self):
    return str(self.labelname)


class UserProfile(models.Model):
  """Extra per-User information."""
  GENDER_CHOICES = (
    ('male', 'male'),
    ('female', 'female'),
  )
  def __str__(self):
    return "profile for %s" % (self.user,)

  def HasLabel(self, lbl):
    for l in self.labels.all():
      if l.labelname == lbl:
        return True
    return False

  def FacebookProfile(self):
    if 'socialregistration' not in settings.INSTALLED_APPS:
      return None
    qs = self.user.facebookprofile_set.all()
    if qs:
      return qs[0]

  def MugshotUrl(self):
    if self.mugshot:
      img_url = self.mugshot.image.url
    else:
      args = ('images/unknown-drinker.png',)
      img_url = urlresolvers.reverse('site-media', args=args)
    return img_url

  user = models.OneToOneField(User)
  gender = models.CharField(max_length=8, choices=GENDER_CHOICES)
  weight = models.FloatField()
  labels = models.ManyToManyField(UserLabel)
  mugshot = models.ForeignKey(UserPicture, blank=True, null=True)

def user_post_save(sender, instance, **kwargs):
  defaults = {
    'weight': kb_common.DEFAULT_NEW_USER_WEIGHT,
    'gender': kb_common.DEFAULT_NEW_USER_GENDER,
  }
  profile, new = UserProfile.objects.get_or_create(user=instance,
      defaults=defaults)
post_save.connect(user_post_save, sender=User)


class KegSize(models.Model):
  """ A convenient table of common Keg sizes """
  def Volume(self):
    return units.Quantity(self.volume_ml, units.RECORD_UNIT)

  def __str__(self):
    return "%s [%.2f gal]" % (self.name, self.Volume().ConvertTo.USGallon)

  name = models.CharField(max_length=128)
  volume_ml = models.FloatField()


class KegTap(models.Model):
  """A physical tap of beer."""
  name = models.CharField(max_length=128)
  meter_name = models.CharField(max_length=128)
  ml_per_tick = models.FloatField(default=(1000.0/2200.0))
  description = models.TextField(blank=True, null=True)
  current_keg = models.ForeignKey('Keg', blank=True, null=True)
  max_tick_delta = models.PositiveIntegerField(default=100)
  temperature_sensor = models.ForeignKey('ThermoSensor', blank=True, null=True)

  def __str__(self):
    return "%s: %s" % (self.meter_name, self.name)

  def Temperature(self):
    if self.temperature_sensor:
      last_rec = self.temperature_sensor.thermolog_set.all().order_by('-time')
      if last_rec:
        return last_rec[0]
    return None


class Keg(models.Model):
  """ Record for each installed Keg. """
  def full_volume(self):
    return self.size.Volume()

  def served_volume(self):
    drinks = Drink.objects.filter(keg__exact=self, status__exact='valid')
    tot = units.Quantity(0, units.RECORD_UNIT)
    for d in drinks:
      tot += d.Volume()
    return tot

  def remaining_volume(self):
    return self.full_volume() - self.served_volume()

  def keg_age(self):
    if self.status == 'online':
      end = datetime.datetime.now()
    else:
      end = self.enddate
    return end - self.startdate

  def is_empty(self):
    return float(self.remaining_volume()) <= 0

  def tap(self):
    q = self.kegtap_set.all()
    if q:
      return q[0]
    return None

  def __str__(self):
    return "Keg #%s - %s" % (self.id, self.type)

  type = models.ForeignKey(bdb.BeerType)
  size = models.ForeignKey(KegSize)
  startdate = models.DateTimeField('start date', default=datetime.datetime.now)
  enddate = models.DateTimeField('end date', default=datetime.datetime.now)
  status = models.CharField(max_length=128, choices=(
     ('online', 'online'),
     ('offline', 'offline'),
     ('coming soon', 'coming soon')))
  description = models.CharField(max_length=256, blank=True, null=True)
  origcost = models.FloatField(default=0, blank=True, null=True)

def _KegPostSave(sender, instance, **kwargs):
  keg = instance
  if keg.status == 'offline':
    last_drink_qs = keg.drink_set.all().order_by('-starttime')
    if len(last_drink_qs):
      last_drink = last_drink_qs[0]
      if keg.enddate != last_drink.endtime:
        keg.enddate = last_drink.endtime
        keg.save()

post_save.connect(_KegPostSave, sender=Keg)


class Drink(models.Model):
  """ Table of drinks records """
  class Meta:
    get_latest_by = "starttime"

  def Volume(self):
    return units.Quantity(self.volume_ml, units.RECORD_UNIT)

  def GetSession(self):
    return DrinkingSession.SessionForDrink(self)

  def ShortUrl(self):
    domain = Site.objects.get_current().domain
    return 'http://%s/d/%i' % (domain, self.id)

  def calories(self):
    if not self.keg or not self.keg.type:
      return 0
    cal = self.keg.type.calories_oz * self.Volume().ConvertTo.Ounce
    return cal

  def bac(self):
    bacs = self.bac_set.all()
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
  volume_ml = models.FloatField()

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

def _DrinkPostSave(sender, instance, **kwargs):
  BAC.ProcessDrink(instance)
  DrinkingSession.SessionForDrink(instance)

  keg = instance.keg
  if keg:
    if keg.startdate > instance.starttime:
      keg.startdate = instance.starttime
      keg.save()

  user = instance.user
  if user:
    if user.date_joined > instance.starttime:
      user.date_joined = instance.starttime
      user.save()

  user_stats, created = UserStats.objects.get_or_create(user=user)
  user_stats.UpdateStats(instance)

  if instance.keg:
    keg_stats, created = KegStats.objects.get_or_create(keg=keg)
    keg_stats.UpdateStats(instance)

post_save.connect(_DrinkPostSave, sender=Drink)


class AuthenticationToken(models.Model):
  """A secret token to authenticate a user, optionally pin-protected."""
  class Meta:
    unique_together = ("auth_device", "token_value")

  def __str__(self):
    ret = "%s: %s" % (self.auth_device, self.token_value)
    if self.user is not None:
      ret = "%s (%s)" % (ret, self.user.username)
    return ret

  auth_device = models.CharField(max_length=64)
  token_value = models.CharField(max_length=128)
  pin = models.CharField(max_length=256, blank=True, null=True)
  user = models.ForeignKey(User, blank=True, null=True)
  created = models.DateTimeField(auto_now_add=True)
  enabled = models.BooleanField(default=True)
  expires = models.DateTimeField(blank=True, null=True)

  def IsAssigned(self):
    return self.user is not None

  def IsActive(self):
    if not self.enabled:
      return False
    if not self.expires:
      return True
    return datetime.datetime.now() < self.expires


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
    bac_qs = d.bac_set.all()
    if len(bac_qs):
      # Already has a recorded BAC.
      return bac_qs[0]

    try:
      profile = d.user.get_profile()
    except UserProfile.DoesNotExist:
      # can't compute bac if there is no profile
      return
    if profile.HasLabel('__no_bac__'):
      return
    if not d.keg:
      return
    if not d.keg.type.abv:
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
    return b


def find_object_in_window(qset, start, end, window):
  # Match objects containing the start-end range
  matching = qset.filter(
      starttime__lte=start + window,
      endtime__gte=end - window
  )

  if len(matching):
    return matching[0]

  # Match objects ending just before the start
  earlier = qset.filter(
      endtime__gte=(start - window),
      starttime__lt=start,
  )

  if len(earlier):
    return earlier[0]

  # Match objects occuring just after the end
  newer = qset.filter(
      starttime__lte=(end - window),
      endtime__gt=end,
  )

  if len(newer):
    return newer[0]

  return None


class DrinkingSession(models.Model):
  """A collection of contiguous drinks. """
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()
  drinks = models.ManyToManyField(Drink)
  users = models.ManyToManyField(User)
  kegs = models.ManyToManyField(Keg)

  def Volume(self):
    ret = units.Quantity(0, units.RECORD_UNIT)
    for d in self.drinks.all():
      ret += d.Volume()
    return ret

  def Duration(self):
    return self.endtime - self.startime

  def AddDrink(self, drink):
    dirty = False
    if self.starttime > drink.starttime:
      self.starttime = drink.starttime
      dirty = True
    if self.endtime < drink.endtime:
      self.endtime = drink.endtime
      dirty = True
    self.drinks.add(drink)
    self.users.add(drink.user)
    if drink.keg:
      self.kegs.add(drink.keg)
    if dirty:
      self.save()

    self._UpdateUserPart(drink)

  def _UpdateUserPart(self, drink):
    defaults = {'starttime': drink.starttime, 'endtime': drink.endtime}
    user_part, created = DrinkingSessionUserPart.objects.get_or_create(user=drink.user,
        session=self, defaults=defaults)
    if user_part.starttime > drink.starttime:
      user_part.starttime = drink.starttime
    if user_part.endtime < drink.endtime:
      user_part.endtime = drink.endtime
    user_part.volume_ml += drink.volume_ml
    user_part.save()

  @classmethod
  def SessionForDrink(cls, drink):
    # Return existing session if already assigned.
    q = cls.objects.filter(drinks=drink)
    if q:
      session = q[0]
      return session

    # Return last session if one already exists
    q = cls.objects.all()
    window = datetime.timedelta(minutes=kb_common.DRINK_SESSION_TIME_MINUTES)
    session = find_object_in_window(q, drink.starttime, drink.endtime, window)
    if session:
      session.AddDrink(drink)
      return session

    # Create a new session
    session = cls(starttime=drink.starttime, endtime=drink.endtime)
    session.save()
    session.AddDrink(drink)
    return session


class DrinkingSessionUserPart(models.Model):
  class Meta:
    unique_together = ('session', 'user')
  session = models.ForeignKey(DrinkingSession, related_name='user_parts')
  user = models.ForeignKey(User, related_name='session_parts')
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()
  volume_ml = models.FloatField(default=0)

  def drinks(self):
    return session.drinks.filter(users=user)

  def Volume(self):
    return units.Quantity(self.volume_ml, units.RECORD_UNIT)

class ThermoSensor(models.Model):
  raw_name = models.CharField(max_length=256)
  nice_name = models.CharField(max_length=128)

  def __str__(self):
    return self.nice_name


class Thermolog(models.Model):
  """ A log from an ITemperatureSensor device of periodic measurements. """
  sensor = models.ForeignKey(ThermoSensor)
  temp = models.FloatField()
  time = models.DateTimeField()

  def __str__(self):
    return '%s %.2f C / %.2f F [%s]' % (self.sensor, self.TempC(),
        self.TempF(), self.time)

  def TempC(self):
    return self.temp

  def TempF(self):
    return util.CtoF(self.temp)

  def save(self, force_insert=False, force_update=False):
    super(Thermolog, self).save(force_insert, force_update)
    self._AddToDailyLog()

  def _AddToDailyLog(self):
    # TODO(mikey): prevent termolog entries from being changed; if a particular
    # record is saved more than once, the average temperature will be invalid.
    daily_date = datetime.datetime(year=self.time.year,
        month=self.time.month,
        day=self.time.day)
    defaults = {
        'num_readings': 0,
        'min_temp': self.temp,
        'max_temp': self.temp,
        'mean_temp': 0,
    }
    daily_log, created = ThermoSummaryLog.objects.get_or_create(
        sensor=self.sensor,
        period='daily',
        date=daily_date,
        defaults=defaults)
    if created:
      daily_log.mean_temp = self.temp
    else:
      new_mean = daily_log.num_readings * daily_log.mean_temp + self.temp
      new_mean /= daily_log.num_readings + 1
      daily_log.mean_temp = new_mean

    daily_log.num_readings += 1

    if self.temp > daily_log.max_temp:
      daily_log.max_temp = self.temp
    if self.temp < daily_log.min_temp:
      daily_log.min_temp = self.temp

    daily_log.save()


  @classmethod
  def CompressLogs(cls):
    now = datetime.datetime.now()

    # keep at least the most recent 24 hours
    keep_time = now - datetime.timedelta(hours=24)

    # round down to the start of the day
    keep_date = datetime.datetime(year=keep_time.year, month=keep_time.month,
        day=keep_time.day)

    print "Compressing thermo logs prior to", keep_date

    def _LogGroup(sensor, records):
      num_readings = len(records)
      temps = [x.temp for x in records]
      min_temp = min(temps)
      max_temp = max(temps)
      sum_temps = sum(temps)
      mean_temp = sum_temps / num_readings

      base_date = records[0].time
      daily_date = datetime.datetime(year=base_date.year,
          month=base_date.month, day=base_date.day)

      print "%s\t%s\t%s\t%s\t%s" % (daily_date, num_readings, min_temp, max_temp,
          mean_temp)
      try:
        ThermoSummaryLog.objects.get(date=daily_date, period='daily')
        # Oops! Group already exists
        print "Warning: log already exists for", daily_date
        return
      except ThermoSummaryLog.DoesNotExist:
        pass
      new_rec = ThermoSummaryLog.objects.create(
          sensor=sensor,
          date=daily_date,
          period='daily',
          num_readings=num_readings,
          min_temp=min_temp,
          max_temp=max_temp,
          mean_temp=mean_temp)

    for sensor in ThermoSensor.objects.all():
      old_entries = sensor.thermolog_set.filter(time__lt=keep_date).order_by('time')

      group = []
      group_date = None
      for entry in old_entries:
        entry_date = datetime.datetime(year=entry.time.year,
            month=entry.time.month, day=entry.time.day)
        if group_date is None:
          group_date = entry_date
        if group_date == entry_date:
          group.append(entry)
        else:
          _LogGroup(sensor, group)
          group = [entry]
          group_date = entry_date

      if group:
        _LogGroup(sensor, group)

      old_entries.delete()


class ThermoSummaryLog(models.Model):
  """A summarized temperature sensor log."""
  PERIOD_CHOICES = (
    ('daily', 'daily'),
  )
  sensor = models.ForeignKey(ThermoSensor)
  date = models.DateTimeField()
  period = models.CharField(max_length=64, choices=PERIOD_CHOICES,
      default='daily')
  num_readings = models.PositiveIntegerField()
  min_temp = models.FloatField()
  max_temp = models.FloatField()
  mean_temp = models.FloatField()


class RelayLog(models.Model):
  """ A log from an IRelay device of relay events/ """
  name = models.CharField(max_length=128)
  status = models.CharField(max_length=32)
  time = models.DateTimeField()


class Config(models.Model):
  def __str__(self):
    return '%s=%s' % (self.key, self.value)

  key = models.CharField(max_length=255, unique=True)
  value = models.TextField()

  @classmethod
  def get(cls, key, default=None):
    try:
      return cls.objects.get(key=key)
    except cls.DoesNotExist:
      return default


class _StatsModel(models.Model):
  STATS_BUILDER = None
  class Meta:
    abstract = True
  date = models.DateTimeField(default=datetime.datetime.now)
  stats = fields.JSONField()
  revision = models.PositiveIntegerField(default=0)

  def UpdateStats(self, obj):
    builder = self.STATS_BUILDER()
    # TODO(mikey): use prev
    self.stats = builder.Build(obj)
    self.revision = builder.REVISION
    self.save()


class UserStats(_StatsModel):
  STATS_BUILDER = stats.DrinkerStatsBuilder
  user = models.ForeignKey(User, unique=True, related_name='stats')
  def __str__(self):
    return 'UserStats for %s' % self.user


class KegStats(_StatsModel):
  STATS_BUILDER = stats.KegStatsBuilder
  keg = models.ForeignKey(Keg, unique=True, related_name='stats')
  def __str__(self):
    return 'KegStats for %s' % self.keg


#class ActivityLog(models.Model):
#  name = models.CharField(max_length=255)
#  date = models.DateTimeField(default=datetime.datetime.now)
#  content_type = models.ForeignKey(ContentType, blank=True, null=True)
#  object_id = models.PositiveIntegerField(blank=True, null=True)
#  content_object = generic.GenericForeignKey('content_type', 'object_id',
#      blank=True, null=True)
