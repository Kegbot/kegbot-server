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

"""Dump/restore utility methods for Kegbot."""

import sys

from pykeg.core import kbjson
from pykeg.core import models
from pykeg.proto import protolib

from pykeg.beerdb import models as bdb_models

def _no_log(msg):
  pass

def dump(output_fp, kbsite, indent=None, log_cb=_no_log):
  """Produce a dump of this Kegbot system to the given filestream.

  In its current format, the dump is plaintext JSON string consisting of all
  important data, including tap configuration, drink history, and user account
  details.

  All "derived" tables are NOT backed up.  These are tables with data that can
  be regenerated at any time without any loss of history.  Specifically:
    - session chunks
    - user session chunks
    - keg session chunks
    - keg stats
    - user stats
    - session stats
    - system events
  """
  res = {}
  items = (
      ('bdb_brewers', bdb_models.Brewer.objects.all()),
      ('bdb_styles', bdb_models.BeerStyle.objects.all()),
      ('bdb_beertypes', bdb_models.BeerType.objects.all()),
      ('thermosensors', kbsite.thermosensors.all().order_by('id')),
      ('kegs', kbsite.kegs.all().order_by('id')),
      ('taps', kbsite.taps.all().order_by('id')),
      ('sessions', kbsite.sessions.all().order_by('id')),
      ('thermologs', kbsite.thermologs.all().order_by('-id')[:60*24]),
      ('thermosummarylogs', kbsite.thermosummarylogs.all().order_by('id')),
      ('users', models.User.objects.all().order_by('id')),
      ('profiles', models.UserProfile.objects.all().order_by('id')),
      ('drinks', kbsite.drinks.valid().order_by('id')),
      ('tokens', kbsite.tokens.all().order_by('id')),
  )

  log_cb('Generating backup data ...')
  for name, qs in items:
    log_cb('  .. dumping %s' % name)
    res[name] = list(protolib.ToDict(qs, full=True))

  log_cb('Serializing and writing backup data ...')
  output_fp.write(kbjson.dumps(res, indent=indent))

def restore(input_fp, kbsite, log_cb=_no_log):
  def _log(obj):
    obj_cls = obj.__class__
    obj_name = obj_cls.__name__
    log_cb('  +++ %s: %s' % (obj_name, obj))

  data = kbjson.loads(input_fp.read())

  brewer_map = {}
  for rec in data.get('bdb_brewers', []):
    try:
      brewer = bdb_models.Brewer.objects.get(id=rec.id)
    except bdb_models.Brewer.DoesNotExist:
      brewer = bdb_models.Brewer(id=rec.id)
    brewer.name = rec.name
    brewer.country = rec.get('country')
    brewer.origin_state = rec.get('origin_state')
    brewer.origin_city = rec.get('origin_city')
    brewer.production = rec.production
    brewer.url = rec.get('url')
    brewer.description = rec.get('description')
    brewer.save()
    _log(brewer)
    brewer_map[rec.id] = brewer

  style_map = {}
  for rec in data.get('bdb_styles', []):
    try:
      style = bdb_models.BeerStyle.objects.get(id=rec.id)
    except bdb_models.BeerStyle.DoesNotExist:
      style = bdb_models.BeerStyle(id=rec.id)
    style.name = rec.name
    style.save()
    _log(style)
    style_map[rec.id] = style

  type_map = {}
  for rec in data.get('bdb_beertypes', []):
    try:
      btype = bdb_models.BeerType.objects.get(id=rec.id)
    except bdb_models.BeerType.DoesNotExist:
      btype = bdb_models.BeerType(id=rec.id)
    btype.name = rec.name
    btype.brewer = brewer_map[rec.brewer_id]
    btype.style = style_map[rec.style_id]
    btype.edition = rec.get('edition')
    btype.abv = rec.get('abv')
    btype.calories_oz = rec.get('calories_oz')
    btype.carbs_oz = rec.get('carbs_oz')
    btype.save()
    _log(btype)
    type_map[rec.id] = btype

  kbsite.thermosensors.all().delete()
  for rec in data.get('thermosensors', []):
    sensor = models.ThermoSensor(site=kbsite, seqn=int(rec.id))
    sensor.raw_name = rec.sensor_name
    sensor.nice_name = rec.nice_name
    sensor.save()
    _log(sensor)

  kbsite.kegs.all().delete()
  for rec in data['kegs']:
    keg = models.Keg(site=kbsite, seqn=int(rec.id))
    keg.type = type_map[rec.type_id]
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
    _log(keg)

  kbsite.taps.all().delete()
  for rec in data['taps']:
    tap = models.KegTap(site=kbsite, seqn=int(rec.id))
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
    _log(tap)

  kbsite.sessions.all().delete()
  for rec in data.get('sessions', []):
    session = models.DrinkingSession(site=kbsite, seqn=int(rec.id))
    session.starttime = rec.start_time
    session.endtime = rec.end_time
    session.volume_ml = rec.volume_ml
    session.name = rec.get('name')
    session.slug = rec.get('slug')
    session.save()
    _log(session)

  for rec in data.get('thermologs', []):
    log = models.Thermolog(site=kbsite, seqn=int(rec.id))
    log.sensor = models.ThermoSensor.objects.get(site=kbsite, seqn=int(rec.sensor_id))
    log.temp = rec.temperature_c
    log.time = rec.record_time
    log.save()
    _log(log)

  kbsite.thermosummarylogs.all().delete()
  for rec in data.get('thermosummarylogs', []):
    log = models.ThermoSummaryLog(site=kbsite, seqn=int(rec.sensor_id))
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
    _log(log)

  user_map = {}
  for rec in data.get('users', []):
    user = None

    # If there's already a user registered with this e-mail address, use it.
    if rec.email:
      user_qs = models.User.objects.filter(email=rec.email)
      if user_qs.count():
        user = user_qs[0]
        user_map[rec.username] = user
        _log(user)
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
    _log(user)

  for rec in data.get('profiles', []):
    user = user_map.get(rec.username)
    if not user:
      print 'Warning: profile for non-existant user: %s' % rec.username
      continue
    profile, created = models.UserProfile.objects.get_or_create(user=user)
    profile.gender = rec.gender
    profile.weight = rec.weight
    profile.save()
    _log(profile)

  kbsite.tokens.all().delete()
  for rec in data.get('tokens', []):
    token = models.AuthenticationToken(site=kbsite, seqn=int(rec.id))
    token.auth_device = rec.auth_device
    token.token_value = rec.token_value
    username = rec.get('username')
    if username:
      token.user = user_map[username]
    token.enabled = rec.enabled
    token.created = rec.created_time
    token.pin = rec.get('pin')
    token.save()
    _log(token)

  kbsite.drinks.all().delete()
  for rec in data.get('drinks', []):
    drink = models.Drink(site=kbsite, seqn=int(rec.id))
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
    _log(drink)

  log_cb('Regenerating sessions ...')
  _RegenSessions(kbsite)
  log_cb('Regenerating stats ...')
  _RegenStats(kbsite)
  log_cb('Regenerating events ...')
  _RegenEvents(kbsite)

def _RegenSessions(kbsite):
  for d in kbsite.drinks.valid().order_by('starttime'):
    d.session.AddDrink(d)

def _RegenStats(kbsite):
  models.SystemStats.objects.filter(site=kbsite).delete()
  models.UserStats.objects.filter(site=kbsite).delete()
  models.KegStats.objects.filter(site=kbsite).delete()
  models.SessionStats.objects.filter(site=kbsite).delete()
  for d in kbsite.drinks.valid().order_by('starttime'):
    d._UpdateSystemStats()
    d._UpdateUserStats()
    d._UpdateKegStats()
    d._UpdateSessionStats()

def _RegenEvents(kbsite):
  kbsite.events.all().delete()
  for d in kbsite.drinks.valid().order_by('starttime'):
    models.SystemEvent.ProcessDrink(d)
