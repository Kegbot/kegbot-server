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
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from pykeg.core import kb_common
from pykeg.core import units
from pykeg.core import util

SCHEMA_VERSION = 22

# This is a Django models definition for the kegbot database

class UserPicture(models.Model):
  def __str__(self):
    return "%s UserPicture" % (self.user,)

  user = models.OneToOneField(User)
  image = models.ImageField(upload_to='mugshots')
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

  user = models.OneToOneField(User)
  gender = models.CharField(max_length=8, choices=GENDER_CHOICES)
  weight = models.FloatField()
  labels = models.ManyToManyField(UserLabel)
  #mugshot = models.ForeignKey(UserPicture, blank=True, null=True)

def user_post_save(sender, instance, **kwargs):
  defaults = {
    'weight': kb_common.DEFAULT_NEW_USER_WEIGHT,
    'gender': kb_common.DEFAULT_NEW_USER_GENDER,
  }
  profile, new = UserProfile.objects.get_or_create(user=instance,
      defaults=defaults)
models.signals.post_save.connect(user_post_save, sender=User)


class Brewer(models.Model):
  name = models.CharField(max_length=128)
  origin_country = models.CharField(max_length=128, default='')
  origin_state = models.CharField(max_length=128, default='')
  origin_city = models.CharField(max_length=128, default='', blank=True,
      null=True)
  distribution = models.CharField(max_length=128,
      choices = ( ('retail', 'retail'),
                  ('homebrew', 'homebrew'),
                  ('unknown', 'unknown'),
      ),
      default = 'unknown',
  )
  url = models.URLField(verify_exists=False, default='', blank=True, null=True)
  comment = models.TextField(default='', blank=True, null=True)

  def __str__(self):
    return "%s (%s, %s, %s)" % (self.name, self.origin_city,
                                self.origin_state, self.origin_country)


class BeerStyle(models.Model):
  name = models.CharField(max_length=128)

  def __str__(self):
    return self.name


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


class KegSize(models.Model):
  """ A convenient table of common Keg sizes """
  def Volume(self):
    return units.Quantity(self.volume, units.RECORD_UNIT)

  def __str__(self):
    return "%s [%.2f gal]" % (self.name, self.Volume().ConvertTo.USGallon)

  name = models.CharField(max_length=128)
  volume = models.IntegerField()


class KegTap(models.Model):
  """A physical tap of beer."""
  name = models.CharField(max_length=128)
  meter_name = models.CharField(max_length=128)
  description = models.TextField(blank=True, null=True)
  current_keg = models.ForeignKey('Keg', blank=True, null=True)


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

  def __str__(self):
    return "Keg #%s - %s" % (self.id, self.type)

  type = models.ForeignKey(BeerType)
  size = models.ForeignKey(KegSize)
  startdate = models.DateTimeField('start date', default=datetime.datetime.now)
  enddate = models.DateTimeField('end date', default=datetime.datetime.now)
  channel = models.IntegerField()  ### FIXME: deprecated
  status = models.CharField(max_length=128, choices=(
     ('online', 'online'),
     ('offline', 'offline'),
     ('coming soon', 'coming soon')))
  description = models.CharField(max_length=256)
  origcost = models.FloatField(default=0)


class Drink(models.Model):
  """ Table of drinks records """
  class Meta:
    get_latest_by = "starttime"

  def Volume(self):
    return units.Quantity(self.volume, units.RECORD_UNIT)

  def GetSession(self):
    q = self.userdrinkingsessionassignment_set.all()
    if q.count() == 1:
      return q[0].session
    return None

  def GetGroup(self):
    sess = self.GetSession()
    if sess:
      return sess.group
    return None

  def ShortUrl(self):
    domain = Site.objects.get_current().domain
    return 'http://%s/d/%i' % (domain, self.id)

  def calories(self):
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


class UserDrinkingSession(models.Model):
  """ A derived table grouping a sequence of drinks by a user.

  A single row of this table exists for one or more UserDrinkingSessionAssignment
  rows to point at.
  """
  user = models.ForeignKey(User)
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()
  group = models.ForeignKey('DrinkingSessionGroup')

  def UpdateTimes(self, drink):
    if self.starttime > drink.starttime:
      self.starttime = drink.starttime
    if self.endtime < drink.endtime:
      self.endtime = drink.endtime

  def GetDrinks(self):
    return (a.drink for a in self.userdrinkingsessionassignment_set.all())

  def Volume(self):
    tot = units.Quantity(0, units.RECORD_UNIT)
    for d in self.GetDrinks():
      tot += d.Volume()
    return tot

  @classmethod
  def CreateOrUpdateSessionForDrink(cls, d):
    """ Create or update a UserDrinkingSession given a drink """
    window = datetime.timedelta(minutes=kb_common.DRINK_SESSION_TIME_MINUTES)

    qset = d.user.userdrinkingsession_set
    session = find_object_in_window(qset, d.starttime, d.endtime, window)
    if not session:
      session = UserDrinkingSession(user=d.user, starttime=d.starttime,
                                    endtime=d.endtime)

    session.UpdateTimes(d)
    session.group = DrinkingSessionGroup.Assign(session)
    session.save()

    return session


class UserDrinkingSessionAssignment(models.Model):
  drink = models.ForeignKey(Drink)
  session = models.ForeignKey(UserDrinkingSession)

  @classmethod
  def RecordDrink(cls, d):
    """ Create a new record for the drink |d|.

    This method calles UserDrinkingSession.CreateOrUpdateSessionForDrink to find or
    create a UserDrinkingSession matching this drink.
    """
    session = UserDrinkingSession.CreateOrUpdateSessionForDrink(d)
    UserDrinkingSessionAssignment.objects.filter(drink=d).delete()
    dg = UserDrinkingSessionAssignment(
        drink=d,
        session=session)
    dg.save()
    return dg


class DrinkingSessionGroup(models.Model):
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()

  def UpdateTimes(self, session):
    if self.starttime > session.starttime:
      self.starttime = session.starttime
    if self.endtime < session.endtime:
      self.endtime = session.endtime

  def TotalVolume(self):
    tot = units.Quantity(0, units.RECORD_UNIT)
    for sess in self.GetSessions():
      tot += sess.Volume()
    return tot

  def GetSessions(self):
    return self.userdrinkingsession_set.all()

  def GetUsers(self):
    return set(sess.user for sess in self.GetSessions())

  @classmethod
  def Assign(self, session):
    window = datetime.timedelta(minutes=kb_common.GROUP_SESSION_TIME_MINUTES)
    group = find_object_in_window(DrinkingSessionGroup.objects.all(),
                                  session.starttime, session.endtime, window)
    if not group:
      group = DrinkingSessionGroup(starttime=session.starttime,
                                   endtime=session.endtime)

    group.UpdateTimes(session)
    group.save()

    return group


class Thermolog(models.Model):
  """ A log from an ITemperatureSensor device of periodic measurements. """
  name = models.CharField(max_length=128)
  temp = models.FloatField()
  time = models.DateTimeField()

  def __str__(self):
    degf = util.CtoF(self.temp)
    return '%s %.2f C / %.2f F [%s]' % (self.name, self.temp, degf, self.time)


class RelayLog(models.Model):
  """ A log from an IRelay device of relay events/ """
  name = models.CharField(max_length=128)
  status = models.CharField(max_length=32)
  time = models.DateTimeField()


class Config(models.Model):
  def __str__(self):
    return '%s=%s' % (self.key, self.value)

  key = models.CharField(max_length=256, unique=True)
  value = models.TextField()

  @classmethod
  def get(cls, key, default=None):
    try:
      return cls.objects.get(key=key)
    except cls.DoesNotExist:
      return default
