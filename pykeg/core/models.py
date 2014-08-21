# -*- coding: latin-1 -*-
# Copyright 2014 Bevbot LLC, All Rights Reserved
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

from __future__ import absolute_import

import datetime
import logging
import os
import pytz
import random
import re
import urlparse
from uuid import uuid4
from distutils.version import StrictVersion

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.core.urlresolvers import reverse
from django.core import validators
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.utils import timezone

from imagekit.models import ImageSpecField
from imagekit.processors import Adjust
from imagekit.processors import resize

from pykeg.backend import get_kegbot_backend
from pykeg.core import colors
from pykeg.core import kb_common
from pykeg.core import keg_sizes
from pykeg.core import fields
from pykeg.core import managers
from pykeg.core.util import get_version
from pykeg.util.email import build_message

from kegbot.util import kbjson
from kegbot.util import units
from kegbot.util import util

from pykeg.core.jsonfield import JSONField
from django.utils.translation import ugettext_lazy as _

"""Django models definition for the kegbot database."""

TIMEZONE_CHOICES = ((z, z) for z in pytz.common_timezones)

logger = logging.getLogger(__name__)


class User(AbstractBaseUser):
    """A customized User model based on auth.User.

    Differs from (and does not inherit) AbstractUser because this model:
        - Does not use groups/permissions.
        - Drops `first_name` and `last_name`.
    """

    ### Django AbstractUser fields.

    is_superuser = models.BooleanField(_('superuser status'), default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.'))

    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
    ])
    display_name = models.CharField(default='', max_length=127,
        help_text='Full name, will be shown in some places instead of username')

    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    ### Kegbot fields.

    mugshot = models.ForeignKey('Picture', blank=True, null=True,
        related_name='user_mugshot',
        on_delete=models.SET_NULL)
    activation_key = models.CharField(max_length=128, blank=True,
        null=True,
        help_text='Unguessable token, used to finish registration.')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
        return self.username

    ### Django-required methods.

    def get_full_name(self):
        return self.display_name

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    ### Other methods.

    def get_absolute_url(self):
        return reverse('kb-drinker', kwargs={'username': self.username})

    def is_guest(self):
        return self.username == 'guest'

    def get_stats(self):
        return Stats.get_latest_for_view(user=self)

    def get_api_key(self):
        api_key, new = ApiKey.objects.get_or_create(user=self,
            defaults={'key': ApiKey.generate_key()})
        return api_key.key


def _user_pre_save(sender, instance, **kwargs):
    user = instance
    if not user.display_name:
        user.display_name = user.username

pre_save.connect(_user_pre_save, sender=User)


class Invitation(models.Model):
    """A time-sensitive cookie which can be used to create an account."""
    invite_code = models.CharField(unique=True, max_length=255,
        default=lambda: str(uuid4()),
        help_text='Unguessable token which must be presented to use this invite')
    for_email = models.EmailField(
        help_text='Address this invitation was sent to.')
    invited_date = models.DateTimeField(_('date invited'), auto_now_add=True,
        help_text='Date and time the invitation was sent')
    expires_date = models.DateTimeField(_('date expries'),
        default=lambda: timezone.now() + datetime.timedelta(hours=24),
        help_text='Date and time after which the invitation is considered expired')
    invited_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL,
        help_text='User that created this invitation, if any.')

    def is_expired(self, now=None):
        if now is None:
            now = timezone.now()
        return now > self.expires_date

    def send(self):
        site = KegbotSite.get()
        base_url = site.reverse_full('registration_register')
        url = base_url + '?invite_code=' + self.invite_code
        context = {
            'site_name': site.title,
            'url': url,
        }
        message = build_message(self.for_email, 'registration/email_invite.html', context)
        if message:
            message.send(fail_silently=True)


class KegbotSite(models.Model):

    VOLUME_DISPLAY_UNITS_CHOICES = (
        ('metric', 'Metric (mL, L)'),
        ('imperial', 'Imperial (oz, pint)'),
    )
    TEMPERATURE_DISPLAY_UNITS_CHOICES = (
        ('f', 'Fahrenheit'),
        ('c', 'Celsius'),
    )
    PRIVACY_CHOICES = (
        ('public', 'Public: Browsing does not require login'),
        ('members', 'Members only: Must log in to browse'),
        ('staff', 'Staff only: Only logged-in staff accounts may browse'),
    )
    REGISTRATION_MODE_CHOICES = (
        ('public', 'Public: Anyone can register.'),
        ('member-invite-only', 'Member Invite: Must be invited by an existing member.'),
        ('staff-invite-only', 'Staff Invite Only: Must be invited by a staff member.'),
    )
    DEFAULT_PRIVACY = 'public'
    DEFAULT_REGISTRATION_MODE = 'public'

    name = models.CharField(max_length=64, unique=True, default='default',
        editable=False)
    server_version = models.CharField(max_length=64, null=True, editable=False)
    is_setup = models.BooleanField(default=False,
        help_text='True if the site has completed setup.',
        editable=False)
    registration_id = models.TextField(max_length=128, editable=False,
        blank=True, default='',
        help_text='A unique id for this system.')

    volume_display_units = models.CharField(max_length=64,
        choices=VOLUME_DISPLAY_UNITS_CHOICES, default='imperial',
        help_text='Unit system to use when displaying volumetric data.')
    temperature_display_units = models.CharField(max_length=64,
        choices=TEMPERATURE_DISPLAY_UNITS_CHOICES, default='f',
        help_text='Unit system to use when displaying temperature data.')
    title = models.CharField(max_length=64, default='My Kegbot',
        help_text='The title of this site.')
    background_image = models.ForeignKey('Picture', blank=True, null=True,
        on_delete=models.SET_NULL,
        help_text='Background for this site.')
    google_analytics_id = models.CharField(blank=True, null=True, max_length=64,
        help_text='Set to your Google Analytics ID to enable tracking. '
        'Example: UA-XXXX-y')
    session_timeout_minutes = models.PositiveIntegerField(
        default=kb_common.DRINK_SESSION_TIME_MINUTES,
        help_text='Maximum time, in minutes, that a session may be idle (no pours) '
        'before it is considered to be finished.  '
        'Recommended value is %s.' % kb_common.DRINK_SESSION_TIME_MINUTES)
    privacy = models.CharField(max_length=63, choices=PRIVACY_CHOICES,
        default=DEFAULT_PRIVACY,
        help_text='Who can view Kegbot data?')
    registration_mode = models.CharField(max_length=63, choices=REGISTRATION_MODE_CHOICES,
        default=DEFAULT_REGISTRATION_MODE,
        help_text='Who can join this Kegbot from the web site?')
    timezone = models.CharField(max_length=255, choices=TIMEZONE_CHOICES,
        default='UTC',
        help_text='Time zone for this system.')

    check_for_updates = models.BooleanField(default=True,
        help_text='Periodically check for updates '
        '(<a href="https://kegbot.org/about/checkin">more info</a>)')

    def __unicode__(self):
        return self.name

    @classmethod
    def get(cls):
        """Gets the default site settings."""
        return KegbotSite.objects.get_or_create(name='default',
            defaults={'is_setup': False, 'server_version': get_version()})[0]

    @classmethod
    def get_installed_version(cls):
        """Returns currently-installed version, or None if not installed."""
        rows = cls.objects.filter(name='default').values('server_version')
        if not rows:
            return None
        return StrictVersion(rows[0].get('server_version', '0.0.0'))

    def get_stats(self):
        return Stats.get_latest_for_view()

    def get_session_timeout_timedelta(self):
        return datetime.timedelta(minutes=self.session_timeout_minutes)

    def base_url(self):
        """Returns the base address of this system."""
        return get_kegbot_backend().get_base_url()

    def full_url(self, path):
        """Returns an absolute URL to the specified path."""
        return urlparse.urljoin(self.base_url(), path)

    def reverse_full(self, *args, **kwargs):
        """Returns an absolute URL to the path reversed by parameters."""
        return self.full_url(reverse(*args, **kwargs))

    def format_volume(self, volume_ml):
        if self.volume_display_units == 'metric':
            if volume_ml < 500:
                return '%d mL' % int(volume_ml)
            return '%.1f L' % (volume_ml / 1000.0)
        else:
            return '%1.f oz' % units.Quantity(volume_ml).InOunces()

    def can_invite(self, user):
        if not user:
            return False
        if self.registration_mode == 'public':
            return True
        if self.registration_mode == 'member-invite-only':
            return not user.is_anonymous()
        if self.registration_mode == 'staff-invite-only':
            return user.is_staff
        return False


class Device(models.Model):
    name = models.CharField(max_length=255, default='Unknown Device')
    created_time = models.DateTimeField(default=timezone.now,
        help_text='Time the device was created.')


class ApiKey(models.Model):
    """Grants access to certain API endpoints to a user via a secret key."""
    user = models.ForeignKey(User, blank=True, null=True,
        help_text='User receiving API access.')
    device = models.ForeignKey(Device, null=True,
        help_text='Device this key is associated with.')
    key = models.CharField(max_length=127, editable=False, unique=True,
        default=lambda: ApiKey.generate_key(),
        help_text='The secret key.')
    active = models.BooleanField(default=True,
        help_text='Whether access by this key is currently allowed.')
    description = models.TextField(blank=True, null=True,
        help_text='Information about this key.')
    created_time = models.DateTimeField(default=timezone.now,
        help_text='Time the key was created.')

    def is_active(self):
        """Returns true if both the key and the key's user are active."""
        return self.active and (not self.user or self.user.is_active)

    def regenerate(self):
        """Discards and regenerates the key."""
        self.key = self.generate_key()
        self.save()

    @classmethod
    def generate_key(cls):
        """Returns a new random key."""
        return '%032x' % random.randint(0, 2 ** 128 - 1)


def _sitesettings_post_save(sender, instance, **kwargs):
    # Privacy settings may have changed.
    cache.clear()
post_save.connect(_sitesettings_post_save, sender=KegbotSite)


class BeverageProducer(models.Model):
    """Information about a beverage producer (brewer, vineyard, etc)."""
    name = models.CharField(max_length=255,
        help_text='Name of the brewer')
    country = fields.CountryField(default='USA',
        help_text='Country of origin')
    origin_state = models.CharField(max_length=128,
        default='', blank=True, null=True,
        help_text='State of origin, if applicable')
    origin_city = models.CharField(max_length=128, default='', blank=True,
        null=True,
        help_text='City of origin, if known')
    is_homebrew = models.BooleanField(default=False)
    url = models.URLField(default='', blank=True, null=True,
        help_text='Brewer\'s home page')
    description = models.TextField(default='', blank=True, null=True,
        help_text='A short description of the brewer')
    picture = models.ForeignKey('Picture', blank=True, null=True,
        on_delete=models.SET_NULL)

    beverage_backend = models.CharField(max_length=255, blank=True, null=True,
        help_text='Future use.')
    beverage_backend_id = models.CharField(max_length=255, blank=True, null=True,
        help_text='Future use.')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Beverage(models.Model):
    """Information about a beverage being served (beer, typically)."""
    TYPE_BEER = 'beer'
    TYPE_WINE = 'wine'
    TYPE_SODA = 'soda'
    TYPE_KOMBUCHA = 'kombucha'
    TYPE_OTHER = 'other'

    TYPES = (
        (TYPE_BEER, 'Beer'),
        (TYPE_WINE, 'Wine'),
        (TYPE_SODA, 'Soda'),
        (TYPE_KOMBUCHA, 'Kombucha'),
        (TYPE_OTHER, 'Other/Unknown'),
    )

    name = models.CharField(max_length=255,
        help_text='Name of the beverage, such as "Potrero Pale".')
    producer = models.ForeignKey(BeverageProducer)

    beverage_type = models.CharField(max_length=32,
        choices=TYPES,
        default=TYPE_BEER)
    style = models.CharField(max_length=255, blank=True, null=True,
        help_text='Beverage style within type, eg "Pale Ale", "Pinot Noir".')
    description = models.TextField(blank=True, null=True,
        help_text='Free-form description of the beverage.')

    picture = models.ForeignKey('Picture', blank=True, null=True,
        help_text='Label image.')
    vintage_year = models.DateField(blank=True, null=True,
        help_text='Date of production, for wines or special/seasonal editions')

    abv_percent = models.FloatField(blank=True, null=True,
        help_text='Alcohol by volume, as percentage (0.0-100.0).')
    calories_per_ml = models.FloatField(blank=True, null=True,
        help_text='Calories per mL of beverage.')
    carbs_per_ml = models.FloatField(blank=True, null=True,
        help_text='Carbohydrates per mL of beverage.')

    color_hex = models.CharField(max_length=16, default=colors.DEFAULT_COLOR,
        validators=[
            RegexValidator(
                regex='(^#[0-9a-zA-Z]{3}$)|(^#[0-9a-zA-Z]{6}$)',
                message='Color must start with "#" and include 3 or 6 hex characters, like #123 or #123456.',
                code='bad_color',
            ),
        ],

        help_text='Approximate beverage color')
    original_gravity = models.FloatField(blank=True, null=True,
        help_text='Original gravity (beer only).')
    specific_gravity = models.FloatField(blank=True, null=True,
        help_text='Final gravity (beer only).')
    srm = models.FloatField(blank=True, null=True,
        help_text='Standard Reference Method value (beer only).')
    ibu = models.FloatField(blank=True, null=True,
        help_text='International Bittering Units value (beer only).')
    star_rating = models.FloatField(blank=True, null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text='Star rating for beverage (0: worst, 5: best)')
    untappd_beer_id = models.IntegerField(blank=True, null=True,
        help_text='Untappd.com resource ID (beer only).')

    beverage_backend = models.CharField(max_length=255, blank=True, null=True,
        help_text='Future use.')
    beverage_backend_id = models.CharField(max_length=255, blank=True, null=True,
        help_text='Future use.')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return u'{} by {}'.format(self.name, self.producer)


class KegTap(models.Model):
    """A physical tap of beer."""
    class Meta:
        ordering = ('sort_order', 'id')
    name = models.CharField(max_length=128,
        help_text='The display name for this tap, for example, "Main Tap".')
    description = models.TextField(blank=True, null=True,
        help_text='User-visible description for this tap.')
    current_keg = models.OneToOneField('Keg', blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='current_tap',
        help_text='Keg currently connected to this tap.')
    temperature_sensor = models.ForeignKey('ThermoSensor', blank=True, null=True,
        on_delete=models.SET_NULL,
        help_text='Optional sensor monitoring the temperature at this tap.')
    sort_order = models.PositiveIntegerField(default=0,
        help_text='Position relative to other taps when sorting (0=first).')

    def __unicode__(self):
        return u'{}: {}'.format(self.name, self.current_keg)

    def is_active(self):
        """Returns True if the tap has an active Keg."""
        return self.current_keg is not None

    def current_meter(self):
        """Returns the currently-assigned FlowMeter, or None."""
        try:
            return self.meter
        except FlowMeter.DoesNotExist:
            return None

    def current_toggle(self):
        """Returns the currently-assigned FlowToggle, or None."""
        try:
            return self.toggle
        except FlowToggle.DoesNotExist:
            return None

    def Temperature(self):
        if self.temperature_sensor:
            last_rec = self.temperature_sensor.thermolog_set.all().order_by('-time')
            if last_rec:
                return last_rec[0]
        return None

    @classmethod
    def get_from_meter_name(cls, meter_name):
        try:
            meter = FlowMeter.get_from_meter_name(meter_name)
        except FlowMeter.DoesNotExist, e:
            raise cls.DoesNotExist(e)
        tap = meter.tap
        if not tap:
            raise cls.DoesNotExist('Meter is inactive')
        return tap


class Controller(models.Model):
    name = models.CharField(max_length=128, unique=True,
        help_text='Identifying name for this device; must be unique.')
    model_name = models.CharField(max_length=128, blank=True, null=True,
        help_text='Type of controller (optional).')
    serial_number = models.CharField(max_length=128, blank=True, null=True,
        help_text='Serial number (optional).')

    def __unicode__(self):
        return u'Controller: {}'.format(self.name)


class FlowMeter(models.Model):
    class Meta:
        unique_together = ('controller', 'port_name')
    controller = models.ForeignKey(Controller, related_name='meters',
        help_text='Controller that owns this meter.')
    port_name = models.CharField(max_length=128,
        help_text='Controller-specific data port name for this meter.')
    tap = models.OneToOneField(KegTap, blank=True, null=True,
        related_name='meter',
        help_text='Tap to which this meter is currently bound.')
    ticks_per_ml = models.FloatField(default=kb_common.DEFAULT_TICKS_PER_ML,
        help_text='Flow meter pulses per mL of fluid.  Common values: %s '
        '(SF800), 2.2 (Vision 2000)' % kb_common.DEFAULT_TICKS_PER_ML)

    def meter_name(self):
        return '{}.{}'.format(self.controller.name, self.port_name)

    def __unicode__(self):
        return self.meter_name()

    @classmethod
    def get_or_create_from_meter_name(cls, meter_name):
        try:
            return cls.get_from_meter_name(meter_name)
        except cls.DoesNotExist:
            pass

        idx = meter_name.find('.')
        if idx <= 0:
            raise ValueError('Illegal name')

        controller_name = meter_name[:idx]
        port_name = meter_name[idx + 1:]
        controller = Controller.objects.get_or_create(name=controller_name)[0]
        return cls.objects.get_or_create(controller=controller, port_name=port_name)[0]

    @classmethod
    def get_from_meter_name(cls, meter_name):
        idx = meter_name.find('.')
        if idx <= 0:
            raise cls.DoesNotExist('Illegal meter_name: %s' % repr(meter_name))
        controller_name = meter_name[:idx]
        port_name = meter_name[idx + 1:]

        try:
            controller = Controller.objects.get(name=controller_name)
        except Controller.DoesNotExist:
            raise cls.DoesNotExist('No such controller: %s' % repr(controller_name))

        return cls.objects.get(controller=controller, port_name=port_name)


class FlowToggle(models.Model):
    class Meta:
        unique_together = ('controller', 'port_name')
    controller = models.ForeignKey(Controller, related_name='toggles',
        help_text='Controller that owns this toggle.')
    port_name = models.CharField(max_length=128,
        help_text='Controller-specific data port name for this toggle.')
    tap = models.OneToOneField(KegTap, blank=True, null=True,
        related_name='toggle',
        help_text='Tap to which this toggle is currently bound.')

    def toggle_name(self):
        return u'{}.{}'.format(self.controller.name, self.port_name)

    def __unicode__(self):
        return u'{} (tap: {})'.format(self.toggle_name(), self.tap)

    @classmethod
    def get_or_create_from_toggle_name(cls, toggle_name):
        try:
            return cls.get_from_toggle_name(toggle_name)
        except cls.DoesNotExist:
            pass

        idx = toggle_name.find('.')
        if idx <= 0:
            raise ValueError('Illegal name')

        controller_name = toggle_name[:idx]
        port_name = toggle_name[idx + 1:]
        controller = Controller.objects.get_or_create(name=controller_name)[0]
        return cls.objects.get_or_create(controller=controller, port_name=port_name)[0]

    @classmethod
    def get_from_toggle_name(cls, toggle_name):
        idx = toggle_name.find('.')
        if idx <= 0:
            raise cls.DoesNotExist('Illegal toggle_name: %s' % repr(toggle_name))
        controller_name = toggle_name[:idx]
        port_name = toggle_name[idx + 1:]

        try:
            controller = Controller.objects.get(name=controller_name)
        except Controller.DoesNotExist:
            raise cls.DoesNotExist('No such controller: %s' % repr(controller_name))

        return cls.objects.get(controller=controller, port_name=port_name)


class Keg(models.Model):
    """Record for each physical Keg."""
    type = models.ForeignKey(Beverage,
        on_delete=models.PROTECT,
        help_text='Beverage in this Keg.')
    keg_type = models.CharField(max_length=32,
        choices=keg_sizes.DESCRIPTIONS.items(),
        default=keg_sizes.HALF_BARREL,
        help_text='Keg container type, used to initialize keg\'s full volume')
    served_volume_ml = models.FloatField(default=0, editable=False,
        help_text='Computed served volume.')
    full_volume_ml = models.FloatField(default=0, editable=False,
        help_text='Full volume of this Keg; usually set automatically from keg_type.')
    start_time = models.DateTimeField(default=timezone.now,
        help_text='Time the Keg was first tapped.')
    end_time = models.DateTimeField(default=timezone.now,
        help_text='Time the Keg was finished or disconnected.')
    online = models.BooleanField(default=True, editable=False,
        help_text='True if the keg is currently assigned to a tap.')
    finished = models.BooleanField(default=False, editable=False,
        help_text='True when the Keg has been exhausted or discarded.')
    description = models.CharField(max_length=256, blank=True, null=True,
        help_text='User-visible description of the Keg.')
    spilled_ml = models.FloatField(default=0,
        help_text='Amount of beverage poured without an associated Drink.')
    notes = models.TextField(blank=True, null=True,
        help_text='Private notes about this keg, viewable only by admins.')

    def get_absolute_url(self):
        return reverse('kb-keg', args=(str(self.id),))

    def full_url(self):
        return KegbotSite.get().full_url(self.get_absolute_url())

    def full_volume(self):
        return self.full_volume_ml

    def served_volume(self):
        # Deprecated
        return self.served_volume_ml

    def remaining_volume_ml(self):
        return self.full_volume_ml - self.served_volume_ml - self.spilled_ml

    def percent_full(self):
        result = float(self.remaining_volume_ml()) / float(self.full_volume_ml) * 100
        result = max(min(result, 100), 0)
        return result

    def keg_age(self):
        if self.online:
            end = timezone.now()
        else:
            end = self.end_time
        return end - self.start_time

    def keg_type_description(self):
        return keg_sizes.get_description(self.keg_type)

    def is_empty(self):
        return float(self.remaining_volume_ml()) <= 0

    def previous(self):
        q = Keg.objects.filter(start_time__lt=self.start_time).order_by('-start_time')
        if q.count():
            return q[0]
        return None

    def next(self):
        q = Keg.objects.filter(start_time__gt=self.start_time).order_by('start_time')
        if q.count():
            return q[0]
        return None

    def get_stats(self):
        return Stats.get_latest_for_view(keg=self)

    def Sessions(self):
        sessions_ids = Drink.objects.filter(keg=self.id).values('session').annotate(models.Count('id'))
        pks = [x.get('session') for x in sessions_ids]
        return [DrinkingSession.objects.get(pk=pk) for pk in pks]

    def TopDrinkers(self):
        stats = self.get_stats()
        if not stats:
            return []
        ret = []
        entries = stats.get('volume_by_drinker', {})
        for username, vol in entries.iteritems():
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                continue  # should not happen
            ret.append((vol, user))
        ret.sort(reverse=True)
        return ret

    def __unicode__(self):
        return u'Keg #{} - {}'.format(self.id, self.type)


def _keg_pre_save(sender, instance, **kwargs):
    keg = instance
    # We don't need to do anything if the keg is still online.
    if keg.online:
        return

    # Determine first drink date & set keg start date to it if earlier.
    drinks = keg.drinks.all().order_by('time')
    if drinks:
        drink = drinks[0]
        if drink.time < keg.start_time:
            keg.start_time = drink.time

    # Determine last drink date & set keg end date to it if later.
    drinks = keg.drinks.all().order_by('-time')
    if drinks:
        drink = drinks[0]
        if drink.time > keg.end_time:
            keg.end_time = drink.time

pre_save.connect(_keg_pre_save, sender=Keg)


class Drink(models.Model):
    """ Table of drinks records """
    class Meta:
        get_latest_by = 'time'
        ordering = ('-time',)

    ticks = models.PositiveIntegerField(editable=False,
        help_text='Flow sensor ticks, never changed once recorded.')
    volume_ml = models.FloatField(editable=False,
        help_text='Calculated (or set) Drink volume.')
    time = models.DateTimeField(editable=False,
      help_text='Date and time of pour.')
    duration = models.PositiveIntegerField(blank=True, default=0, editable=False,
        help_text='Time in seconds taken to pour this Drink.')
    user = models.ForeignKey(User, related_name='drinks', editable=False,
        help_text='User responsible for this Drink, or None if anonymous/unknown.')
    keg = models.ForeignKey(Keg, related_name='drinks',
        on_delete=models.PROTECT, editable=False,
        help_text='Keg against which this Drink is accounted.')
    session = models.ForeignKey('DrinkingSession',
        related_name='drinks', null=True, blank=True, editable=False,
        on_delete=models.PROTECT,
        help_text='Session where this Drink is grouped.')
    shout = models.TextField(blank=True, null=True,
        help_text='Comment from the drinker at the time of the pour.')
    tick_time_series = models.TextField(blank=True, null=True, editable=False,
        help_text='Tick update sequence that generated this drink (diagnostic data).')
    picture = models.OneToOneField('Picture', blank=True, null=True,
        on_delete=models.SET_NULL,
        help_text='Picture snapped with this drink.')

    def is_guest_pour(self):
        return self.user is None or self.user.is_guest()

    def get_absolute_url(self):
        return reverse('kb-drink', args=(str(self.id),))

    def short_url(self):
        return KegbotSite.get().reverse_full('kb-drink-short', args=(str(self.id),))

    def Volume(self):
        return units.Quantity(self.volume_ml)

    def calories(self):
        if not self.keg or not self.keg.type:
            return 0
        ounces = self.Volume().InOunces()
        return self.keg.type.calories_oz * ounces

    def __unicode__(self):
        return 'Drink {} by {}'.format(self.id, self.user)


class AuthenticationToken(models.Model):
    """A secret token to authenticate a user, optionally pin-protected."""
    class Meta:
        unique_together = ('auth_device', 'token_value')

    auth_device = models.CharField(max_length=64,
        help_text='Namespace for this token.')
    token_value = models.CharField(max_length=128,
        help_text='Actual value of the token, unique within an auth_device.')
    nice_name = models.CharField(max_length=256, blank=True, null=True,
        help_text='A human-readable alias for the token, for example "Guest Key".')
    pin = models.CharField(max_length=256, blank=True, null=True,
        help_text='A secret value necessary to authenticate with this token.')
    user = models.ForeignKey(User, blank=True, null=True,
        related_name='tokens',
        help_text='User in possession of and authenticated by this token.')
    enabled = models.BooleanField(default=True,
        help_text='Whether this token is considered active.')
    created_time = models.DateTimeField(auto_now_add=True,
        help_text='Date token was first added to the system.')
    expire_time = models.DateTimeField(blank=True, null=True,
        help_text='Date after which token is treated as disabled.')

    def __unicode__(self):
        auth_device = self.auth_device
        if auth_device == 'core.rfid':
            auth_device = 'RFID'
        elif auth_device == 'core.onewire':
            auth_device = 'OneWire'

        ret = u'{} {}'.format(auth_device, self.token_value)
        if self.nice_name:
            ret += u' ({})'.format(self.nice_name)
        return ret

    def get_auth_device(self):
        auth_device = self.auth_device
        if auth_device == 'core.rfid':
            auth_device = 'RFID'
        elif auth_device == 'core.onewire':
            auth_device = 'OneWire'
        return auth_device

    def IsAssigned(self):
        return self.user is not None

    def IsActive(self):
        if not self.enabled:
            return False
        if not self.expire_time:
            return True
        return timezone.now() < self.expire_time


def _auth_token_pre_save(sender, instance, **kwargs):
    if instance.auth_device in kb_common.AUTH_MODULE_NAMES_HEX_VALUES:
        instance.token_value = instance.token_value.lower()

pre_save.connect(_auth_token_pre_save, sender=AuthenticationToken)


class DrinkingSession(models.Model):
    """A collection of contiguous drinks. """
    class Meta:
        get_latest_by = 'start_time'
        ordering = ('-start_time',)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    volume_ml = models.FloatField(default=0)

    objects = managers.SessionManager()
    name = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return 'Session #{}: {}'.format(self.id, self.start_time)

    def Duration(self):
        return self.end_time - self.start_time

    def _AddDrinkNoSave(self, drink):
        session_delta = KegbotSite.get().get_session_timeout_timedelta()
        session_end = drink.time + session_delta

        if self.start_time > drink.time:
            self.start_time = drink.time
        if self.end_time < session_end:
            self.end_time = session_end
        self.volume_ml += drink.volume_ml

    def AddDrink(self, drink):
        self._AddDrinkNoSave(drink)
        self.save()

    def short_url(self):
        return KegbotSite.get().reverse_full('kb-session-short', args=(str(self.id),))

    def full_url(self):
        return KegbotSite.get().full_url(self.get_absolute_url())

    def get_highlighted_picture(self):
        pictures = self.pictures.all().order_by('-time')
        if pictures:
            return pictures[0]
        return None

    def get_non_highlighted_pictures(self):
        pictures = self.pictures.all().order_by('-time')
        if pictures:
            return pictures[1:]
        return []

    def get_absolute_url(self):
        dt = timezone.localtime(self.start_time)
        return reverse('kb-session-detail', args=(), kwargs={
            'year': dt.year,
            'month': dt.month,
            'day': dt.day,
            'pk': self.pk})

    def get_stats(self):
        return Stats.get_latest_for_view(session=self)

    def summarize_drinkers(self):
        stats = self.get_stats()
        volmap = stats.get('volume_by_drinker', {})
        names = [x for x in reversed(sorted(volmap, key=volmap.get))]

        if 'guest' in names:
            guest_trailer = ' (and possibly others)'
        else:
            guest_trailer = ''

        num = len(names)
        if num == 0:
            return 'no known drinkers'
        elif num == 1:
            ret = names[0]
        elif num == 2:
            ret = '{} and {}'.format(*names)
        elif num == 3:
            ret = '{}, {} and {}'.format(*names)
        else:
            if guest_trailer:
                return '%s, %s and at least %i others' % (names[0], names[1], num - 2)
            else:
                return '%s, %s and %i others' % (names[0], names[1], num - 2)

        return '%s%s' % (ret, guest_trailer)

    def GetTitle(self):
        if self.name:
            return self.name
        else:
            if self.id:
                return 'Session %s' % (self.id,)
            else:
                # Not yet saved.
                return 'New Session'

    def IsActiveNow(self):
        return self.IsActive(timezone.now())

    def IsActive(self, now):
        return self.end_time > now

    def Rebuild(self):
        """Recomputes start time, end time, and volume, based on current drinks.

        This method should be called after changing the set of drinks
        belonging to this session.

        This method has no effect on statistics; see stats module.
        """
        self.volume_ml = 0

        drinks = self.drinks.all()
        if not drinks:
            self.delete()
            return

        session_delta = KegbotSite.get().get_session_timeout_timedelta()
        min_time = None
        max_time = None
        for d in drinks:
            self.AddDrink(d)
            if min_time is None or d.time < min_time:
                min_time = d.time
            if max_time is None or d.time > max_time:
                max_time = d.time
        self.start_time = min_time
        self.end_time = max_time + session_delta
        self.save()

    @classmethod
    def AssignSessionForDrink(cls, drink):
        # Return existing session if already assigned.
        if drink.session:
            return drink.session

        # Return last session if one already exists
        q = DrinkingSession.objects.all().order_by('-end_time')[:1]
        if q and q[0].IsActive(drink.time):
            session = q[0]
            session.AddDrink(drink)
            drink.session = session
            drink.save()
            return session

        # Create a new session
        session = cls(start_time=drink.time, end_time=drink.time)
        session.save()
        session.AddDrink(drink)
        drink.session = session
        drink.save()
        return session


class ThermoSensor(models.Model):
    raw_name = models.CharField(max_length=256)
    nice_name = models.CharField(max_length=128)

    def __unicode__(self):
        if self.nice_name:
            return u'{} ({})'.format(self.nice_name, self.raw_name)
        return self.raw_name

    def LastLog(self):
        try:
            return self.thermolog_set.latest()
        except Thermolog.DoesNotExist:
            return None


class Thermolog(models.Model):
    """ A log from an ITemperatureSensor device of periodic measurements. """
    class Meta:
        get_latest_by = 'time'
        ordering = ('-time',)

    sensor = models.ForeignKey(ThermoSensor)
    temp = models.FloatField()
    time = models.DateTimeField()

    def __unicode__(self):
        return u'%.2f C / %.2f F [%s]' % (self.TempC(), self.TempF(), self.time)

    def TempC(self):
        return self.temp

    def TempF(self):
        return util.CtoF(self.temp)


class Stats(models.Model):
    """Derived statistics.

    Multiple "views" of statistics are stored in this table, for example,
    only statistics for a particular user in a particular session.  The view
    is determined by the columns (user, keg, session), any combination of which
    may be null.

    Stats are temporal on a per-drink basis: for every drink that is recorded,
    a new row is generated for each view (2^3 rows total).

    See stats.generate(..) for generation details.
    """
    time = models.DateTimeField(default=timezone.now)
    stats = JSONField(dump_kwargs={'cls': kbjson.JSONEncoder})
    drink = models.ForeignKey(Drink)

    is_first = models.BooleanField(default=False,
        help_text='True if this is the most first record for the view.')

    # Any combination of these fields is allowed.
    user = models.ForeignKey(User, related_name='stats', null=True)
    keg = models.ForeignKey(Keg, related_name='stats', null=True)
    session = models.ForeignKey(DrinkingSession, related_name='stats', null=True)

    class Meta:
        get_latest_by = 'id'
        unique_together = ('drink', 'user', 'keg', 'session')

    @classmethod
    def apply_usernames(cls, stats):
        """Given a stats dictionary, translate numeric user ids to usernames."""
        def safe_get_user(pk):
            try:
                return User.objects.get(pk=pk)
            except (User.DoesNotExist, ValueError):
                return None
        orig = stats.get('registered_drinkers', [])
        if orig:
            stats['registered_drinkers'] = [safe_get_user(pk).username for pk in orig if safe_get_user(pk)]

        orig = stats.get('volume_by_drinker', util.AttrDict())
        if orig:
            stats['volume_by_drinker'] = util.AttrDict(
                (safe_get_user(pk).username, val) for pk, val in orig.iteritems() if safe_get_user(pk))

    @classmethod
    def get_latest_for_view(cls, user=None, keg=None, session=None):
        """Returns the most recent stats data for the (user, keg, session) tuple.

        Returns an empty dict if no stats available for this view.
        """
        try:
            stats = cls.objects.filter(user=user, keg=keg, session=session).order_by('-id')[0].stats
        except IndexError:
            stats = {}
        cls.apply_usernames(stats)
        return util.AttrDict(stats)


class SystemEvent(models.Model):
    class Meta:
        ordering = ('-id',)
        get_latest_by = 'time'

    DRINK_POURED = 'drink_poured'
    SESSION_STARTED = 'session_started'
    SESSION_JOINED = 'session_joined'
    KEG_TAPPED = 'keg_tapped'
    KEG_VOLUME_LOW = 'keg_volume_low'
    KEG_ENDED = 'keg_ended'

    KINDS = (
        (DRINK_POURED, 'Drink poured'),
        (SESSION_STARTED, 'Session started'),
        (SESSION_JOINED, 'User joined session'),
        (KEG_TAPPED, 'Keg tapped'),
        (KEG_VOLUME_LOW, 'Keg volume low'),
        (KEG_ENDED, 'Keg ended'),
    )

    kind = models.CharField(max_length=255, choices=KINDS,
        help_text='Type of event.')
    time = models.DateTimeField(help_text='Time of the event.')
    user = models.ForeignKey(User, blank=True, null=True,
        related_name='events',
        help_text='User responsible for the event, if any.')
    drink = models.ForeignKey(Drink, blank=True, null=True,
        related_name='events',
        help_text='Drink involved in the event, if any.')
    keg = models.ForeignKey(Keg, blank=True, null=True,
        related_name='events',
        help_text='Keg involved in the event, if any.')
    session = models.ForeignKey(DrinkingSession, blank=True, null=True,
        related_name='events',
        help_text='Session involved in the event, if any.')

    objects = managers.SystemEventManager()

    def __unicode__(self):
        if self.kind == self.DRINK_POURED:
            ret = u'Drink {} poured'.format(self.drink.id)
        elif self.kind == self.SESSION_STARTED:
            ret = u'Session {} started by drink {}'.format(self.session.id, self.drink.id)
        elif self.kind == self.SESSION_JOINED:
            ret = u'Session {} joined by {} (drink {})'.format(self.session.id,
                self.user.username, self.drink.id)
        elif self.kind == self.KEG_TAPPED:
            ret = u'Keg {} tapped'.format(self.keg.id)
        elif self.kind == self.KEG_VOLUME_LOW:
            ret = u'Keg {} volume low'.format(self.keg.id)
        elif self.kind == self.KEG_ENDED:
            ret = u'Keg {} ended'.format(self.keg.id)
        else:
            ret = u'Unknown event type ({})'.format(self.kind)
        return u'Event {}: {}'.format(self.id, ret)

    @classmethod
    def build_events_for_keg(cls, keg):
        '''Generates and returns system events for the keg.'''
        events = []
        if keg.online:
            q = keg.events.filter(kind=cls.KEG_TAPPED)
            if q.count() == 0:
                e = keg.events.create(kind=cls.KEG_TAPPED, time=keg.start_time, keg=keg)
                e.save()
                events.append(e)

        if not keg.online:
            q = keg.events.filter(kind=cls.KEG_ENDED)
            if q.count() == 0:
                e = keg.events.create(kind=cls.KEG_ENDED, time=keg.end_time, keg=keg)
                e.save()
                events.append(e)

        return events

    @classmethod
    def build_events_for_drink(cls, drink):
        keg = drink.keg
        session = drink.session
        user = drink.user

        events = cls.build_events_for_keg(keg)

        if session:
            q = session.events.filter(kind=cls.SESSION_STARTED)
            if q.count() == 0:
                e = session.events.create(kind=cls.SESSION_STARTED,
                    time=session.start_time, drink=drink, user=user)
                e.save()
                events.append(e)

        if user:
            q = user.events.filter(kind=cls.SESSION_JOINED, session=session)
            if q.count() == 0:
                e = user.events.create(kind=cls.SESSION_JOINED,
                    time=drink.time, session=session, drink=drink, user=user)
                e.save()
                events.append(e)

        e = drink.events.create(kind=cls.DRINK_POURED,
            time=drink.time, drink=drink, user=user, keg=keg,
            session=session)
        e.save()
        events.append(e)

        volume_now = keg.remaining_volume_ml()
        volume_before = volume_now + drink.volume_ml
        threshold = keg.full_volume_ml * kb_common.KEG_VOLUME_LOW_PERCENT

        if volume_now <= threshold and volume_before > threshold:
            e = drink.events.create(kind=cls.KEG_VOLUME_LOW,
                time=drink.time, drink=drink, user=user, keg=keg,
                session=session)
            e.save()
            events.append(e)

        return events


def _pics_file_name(instance, filename, now=None, uuid_str=None):
    if not now:
        now = timezone.now()
    if not uuid_str:
        uuid_str = str(uuid4()).replace('-', '')
    date_str = now.strftime('%Y%m%d%H%M%S')
    ext = os.path.splitext(filename)[1]
    new_filename = '%s-%s%s' % (date_str, uuid_str, ext)

    return os.path.join('pics', new_filename)


class Picture(models.Model):
    image = models.ImageField(upload_to=_pics_file_name,
        help_text='The image')
    resized = ImageSpecField(source='image',
        processors=[resize.ResizeToFit(1024, 1024)],
        format='JPEG',
        options={'quality': 100})
    resized_png = ImageSpecField(source='image',
        processors=[resize.ResizeToFit(1024, 1024)],
        format='PNG',
        options={'quality': 100})
    thumbnail = ImageSpecField(source='image',
        processors=[Adjust(contrast=1.2, sharpness=1.1), resize.SmartResize(128, 128)],
        format='JPEG',
        options={'quality': 90})
    thumbnail_png = ImageSpecField(source='image',
        processors=[Adjust(contrast=1.2, sharpness=1.1), resize.SmartResize(128, 128)],
        format='PNG',
        options={'quality': 90})

    time = models.DateTimeField(default=timezone.now,
        help_text='Time/date of image capture')
    caption = models.TextField(blank=True, null=True,
        help_text='Caption for the picture, if any.')
    user = models.ForeignKey(User, blank=True, null=True,
        related_name='pictures',
        help_text='User that owns/uploaded this picture')
    keg = models.ForeignKey(Keg, blank=True, null=True,
        related_name='pictures',
        on_delete=models.SET_NULL,
        help_text='Keg this picture was taken with, if any.')
    session = models.ForeignKey(DrinkingSession, blank=True, null=True,
        related_name='pictures',
        on_delete=models.SET_NULL,
        help_text='Session this picture was taken with, if any.')

    def __unicode__(self):
        return u'Picture: {}'.format(self.image)

    def get_caption(self):
        if self.caption:
            return self.caption
        elif self.drink:
            if self.user:
                return u'{} pouring drink {}'.format(self.user.username, self.drink.id)
            else:
                return u'An unknown drinker pouring drink {}'.format(self.drink.id)
        return ''

    def erase_and_delete(self):
        try:
            for spec in ('resized', 'resized_png', 'thumbnail', 'thumbnail_png', 'image'):
                image_file = getattr(self, spec)
                exists = bool(image_file)
                if not exists:
                    logger.debug('erase_and_delete: image.id={} spec={}: does not exist'.format(
                        self.id, spec))
                    continue
                logger.debug('erase_and_delete: image.id={} spec={}: deleting ...'.format(
                    self.id, spec))

                try:
                    try:
                        default_storage.delete(image_file.path)
                    except NotImplementedError:
                        default_storage.delete(image_file.name)
                    logger.debug('erase_and_delete: image.id={} spec={}: deleted'.format(
                        self.id, spec))
                except IOError as e:
                    logger.warning('erase_and_delete: image.id={} spec={}: error: {}'.format(
                        self.id, spec, e))
        finally:
            self.delete()


class NotificationSettings(models.Model):
    """Stores a user's notification settings for a notification backend."""

    class Meta:
        unique_together = ('user', 'backend')

    user = models.ForeignKey(User,
        help_text='User for these settings.')
    backend = models.CharField(max_length=255,
        help_text='Notification backend (dotted path) for these settings.')
    keg_tapped = models.BooleanField(default=True,
        help_text='Sent when a keg is activated.')
    session_started = models.BooleanField(default=False,
        help_text='Sent when a new drinking session starts.')
    keg_volume_low = models.BooleanField(default=False,
        help_text='Sent when a keg becomes low.')
    keg_ended = models.BooleanField(default=False,
        help_text='Sent when a keg has been taken offline.')


class PluginData(models.Model):
    """Key/value JSON data store for plugins."""

    class Meta:
        unique_together = ('plugin_name', 'key')

    plugin_name = models.CharField(max_length=127,
        help_text='Plugin short name')
    key = models.CharField(max_length=127)
    value = JSONField()
