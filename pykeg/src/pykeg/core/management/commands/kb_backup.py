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

import sys

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pykeg.core import kbjson
from pykeg.core import models
from pykeg.core import protolib
from pykeg.core.management.commands.common import progbar

from pykeg.beerdb import models as bdb_models

from optparse import make_option

class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
      make_option('-d', '--dump',
        type='string',
        action='store',
        dest='dump',
        help='Filename to dump to (dump mode).'),
      make_option('-r', '--restore',
        type='string',
        action='store',
        dest='restore',
        help='Filename to restore from (restore mode).'),
      make_option('-i', '--indent',
        action='store_true',
        dest='indent',
        default=True,
        help='Indent and pretty-print the output.'),
      )

  help = """Kegbot dump/restore tool. WARNING: Experimental."""
  args = '<none>'

  def handle(self, **options):
    if not (bool(options['dump']) ^ bool(options['restore'])):
      raise CommandError('Must give exactly one of: --dump=<filename>, --restore=<filename>')

    if options['restore']:
      self.restore(options)
    else:
      self.backup(options)

  def debug(self, msg):
    print msg

  def restore(self, options, delete_first=True):
    self._last_log_cls = None
    kbsite = models.KegbotSite.objects.get(name='default')
    fp = open(options['restore'], 'r')
    data = kbjson.loads(fp.read())
    fp.close()

    for rec in data.get('bdb_brewers', []):
      brewer, created = bdb_models.Brewer.objects.get_or_create(id=rec.id)
      brewer.id = rec.id
      brewer.name = rec.name
      brewer.country = rec.get('country')
      brewer.origin_state = rec.get('origin_state')
      brewer.origin_city = rec.get('origin_city')
      brewer.production = rec.production
      brewer.url = rec.get('url')
      brewer.description = rec.get('description')
      brewer.save()
      self.log(brewer)

    for rec in data.get('bdb_styles', []):
      style, created = bdb_models.BeerStyle.objects.get_or_create(id=rec.id)
      style.name = rec.name
      style.save()
      self.log(style)

    for rec in data.get('bdb_beertypes', []):
      btype = bdb_models.BeerType()
      btype, created = bdb_models.BeerType.objects.get_or_create(id=rec.id)
      btype.id = rec.id
      btype.name = rec.name
      btype.brewer = bdb_models.Brewer.objects.get(pk=rec.brewer_id)
      btype.style = bdb_models.BeerStyle.objects.get(pk=rec.style_id)
      btype.edition = rec.get('edition')
      btype.abv = rec.get('abv')
      btype.calories_oz = rec.get('calories_oz')
      btype.carbs_oz = rec.get('carbs_oz')
      btype.save()
      self.log(btype)

    if delete_first:
      kbsite.thermosensors.all().delete()
    for rec in data.get('thermosensors', []):
      sensor, created = models.ThermoSensor.objects.get_or_create(site=kbsite, seqn=int(rec.id))
      sensor.raw_name = rec.sensor_name
      sensor.nice_name = rec.nice_name
      sensor.save()
      self.log(sensor)

    if delete_first:
      kbsite.kegs.all().delete()
    for rec in data['kegs']:
      keg, created = models.Keg.objects.get_or_create(site=kbsite, seqn=int(rec.id))
      keg.type = bdb_models.BeerType.objects.get(id=rec.type_id)
      keg.startdate = rec.started_time
      keg.enddate = rec.finished_time
      keg.status = rec.status
      keg.description = rec.get('description')
      keg.spilled_ml = rec.spilled_ml

      size, created = models.KegSize.objects.get_or_create(
          name=rec.size_name, volume_ml=rec.size_volume_ml)
      size.save()
      keg.size = size

      keg.save()
      self.log(keg)

    if delete_first:
      kbsite.taps.all().delete()
    for rec in data['taps']:
      tap, created = models.KegTap.objects.get_or_create(site=kbsite, seqn=int(rec.id))
      tap.name = rec.name
      tap.meter_name = rec.meter_name
      tap.ml_per_tick = rec.ml_per_tick
      tap.description = rec.get('description')
      keg_id = int(rec.get('current_keg_id', 0))
      if keg_id:
        tap.current_keg = models.Keg.objects.get(site=kbsite, seqn=keg_id)
      thermo_id = int(rec.get('thermo_sensor_id', 0))
      if thermo_id:
        tap.temperature_sensor = models.ThermoSensor.objects.get(site=kbsite, seqn=thermo_id)
      tap.save()
      self.log(tap)

    if delete_first:
      kbsite.sessions.all().delete()
    for rec in data.get('sessions', []):
      session = models.DrinkingSession(site=kbsite, seqn=int(rec.id))
      session.starttime = rec.start_time
      session.endtime = rec.end_time
      session.volume_ml = rec.volume_ml
      session.name = rec.get('name')
      session.slug = rec.get('slug')
      session.save()
      self.log(session)

    if delete_first:
      kbsite.thermologs.all().delete()
    for rec in data.get('thermologs', []):
      log, created = models.Thermolog.objects.get_or_create(site=kbsite, seqn=int(rec.id))
      log.sensor = models.ThermoSensor.objects.get(site=kbsite, seqn=int(rec.sensor_id))
      log.temp = rec.temperature_c
      log.time = rec.record_time
      log.save()
      self.log(log)

    if delete_first:
      kbsite.thermosummarylogs.all().delete()
    for rec in data.get('thermosummarylogs', []):
      log, created = models.ThermoSummaryLog.objects.get_or_create(site=kbsite,
          seqn=int(rec.sensor_id))
      log.site = kbsite
      log.seqn = rec.id
      log.sensor = models.ThermoSensor.objects.get(site=kbsite, seqn=int(rec.sensor_id))
      log.date = rec.date
      log.period = rec.period
      log.num_readings = rec.num_readings
      log.min_temp = rec.min_temp
      log.max_temp = rec.max_temp
      log.mean_temp = rec.mean_temp
      log.save()
      self.log(log)

    user_map = {}
    for rec in data.get('users', []):
      user = None

      # If there's already a user registered with this e-mail address, use it.
      user_qs = models.User.objects.filter(email=rec.email)
      if user_qs.count():
        user = user_qs[0]
        user_map[rec.username] = user
        self.log(user)
        continue

      # Create a new user, creating a new unique username if necessary.
      iter = 0
      username = rec.username
      while True:
        username_qs = models.User.objects.filter(username=username)
        if not username_qs.count():
          break
        iter += 1
        username = '%s_%i' % (rec.username[:30], iter)

      user = models.User(username=username)
      user.first_name = rec.first_name
      user.last_name = rec.last_name
      user.email = rec.email
      user.password = rec.password
      user.is_active = rec.is_active
      user.last_login = rec.last_login
      user.date_joined = rec.date_joined

      # XXX non-prod
      user.is_staff = rec.is_staff
      user.is_superuser = rec.is_superuser

      user.save()
      user_map[rec.username] = user
      self.log(user)

    for rec in data.get('profiles', []):
      user = user_map.get(rec.username)
      if not user:
        print 'Warning: profile for non-existant user: %s' % rec.username
        continue
      profile, created = models.UserProfile.objects.get_or_create(user=user)
      profile.gender = rec.gender
      profile.weight = rec.weight
      profile.save()
      self.log(profile)

    if delete_first:
      kbsite.tokens.all().delete()
    for rec in data.get('tokens', []):
      token, created = models.AuthenticationToken.objects.get_or_create(site=kbsite, seqn=int(rec.id))
      token.auth_device = rec.auth_device
      token.token_value = rec.token_value
      username = rec.get('username')
      if username:
        token.user = user_map[username]
      token.enabled = rec.enabled
      token.created = rec.created_time
      token.pin = rec.get('pin')
      token.save()
      self.log(token)

    if delete_first:
      kbsite.drinks.all().delete()
    for rec in data.get('drinks', []):
      drink, created = models.Drink.objects.get_or_create(site=kbsite, seqn=int(rec.id))
      drink.ticks = rec.ticks
      drink.volume_ml = rec.volume_ml
      drink.session = models.DrinkingSession.objects.get(site=kbsite, seqn=int(rec.session_id))
      drink.starttime = rec.pour_time
      drink.duration = rec.get('duration')
      drink.status = rec.status
      keg_id = int(rec.get('keg_id', 0))
      if keg_id:
        drink.keg = models.Keg.objects.get(site=kbsite, seqn=keg_id)
      username = rec.get('user_id')
      if username:
        drink.user = user_map[username]
      drink.auth_token = rec.get('auth_token')
      drink.save()
      self.log(drink)

    self._RegenSessions(kbsite)
    self._RegenStats(kbsite)
    self._RegenEvents(kbsite)

  def _RegenSessions(self, kbsite):
    print 'Regenerating sessions ...'
    for d in kbsite.drinks.valid().order_by('starttime'):
      d.session.AddDrink(d)

  def _RegenStats(self, kbsite):
    print 'Regenerating stats ...'
    models.SystemStats.objects.filter(site=kbsite).delete()
    models.UserStats.objects.filter(site=kbsite).delete()
    models.KegStats.objects.filter(site=kbsite).delete()
    models.SessionStats.objects.filter(site=kbsite).delete()
    for d in kbsite.drinks.valid().order_by('starttime'):
      d._UpdateSystemStats()
      d._UpdateUserStats()
      d._UpdateKegStats()
      d._UpdateSessionStats()

  def _RegenEvents(self, kbsite):
    print 'Regenerating events ...'
    kbsite.events.all().delete()
    for d in kbsite.drinks.valid().order_by('starttime'):
      models.SystemEvent.ProcessDrink(d)

  def log(self, obj):
    obj_cls = obj.__class__
    obj_name = obj_cls.__name__

    if obj_cls != self._last_log_cls:
      self._last_log_cls = obj_cls
      sys.stdout.write('\n\n+++%s:\n' % obj_name)
    sys.stdout.write('   %s\n' % obj)
    sys.stdout.flush()

  def backup(self, options):
    kbsite = models.KegbotSite.objects.get(name='default')
    res = {}

    # Things that are not backed up and are instead recomputed:
    #   - session chunks
    #   - user session chunks
    #   - keg session chunks
    #   - keg stats
    #   - user stats
    #   - session stats
    #   - system events
    items = (
        ('bdb_brewers', bdb_models.Brewer.objects.all()),
        ('bdb_styles', bdb_models.BeerStyle.objects.all()),
        ('bdb_beertypes', bdb_models.BeerType.objects.all()),
        ('thermosensors', kbsite.thermosensors.all().order_by('id')),
        ('kegs', kbsite.kegs.all().order_by('id')),
        ('taps', kbsite.taps.all().order_by('id')),
        ('sessions', kbsite.sessions.all().order_by('id')),
        ('thermologs', kbsite.thermologs.all().order_by('id')),
        ('thermosummarylogs', kbsite.thermosummarylogs.all().order_by('id')),
        ('users', models.User.objects.all().order_by('id')),
        ('profiles', models.UserProfile.objects.all().order_by('id')),
        ('drinks', kbsite.drinks.all().order_by('id')),
        ('tokens', kbsite.tokens.all().order_by('id')),
        #('configs', kbsite.configs.all()),
    )

    print 'Generating backup data ...'

    for name, qs in items:
      res[name] = list(protolib.ToProto(qs, full=True))

    print 'Writing backup to %s ...' % options['dump']

    fp = open(options['dump'], 'w')
    indent = None
    if options['indent']:
      indent = 2
    fp.write(kbjson.dumps(res, indent=indent))
    fp.close()

