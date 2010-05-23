# Copyright 2003-2009 Mike Wakerly <opensource@hoho.com>
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
import math

from pykeg.core import backend
from pykeg.core import models
from pykeg.core import units

from pykeg.beerdb import models as bdb

def db_is_installed():
  try:
    models.Config.objects.get(key='db.installed')
    return True
  except models.Config.DoesNotExist:
    return False

def add_label(user, labelname):
  res = models.UserLabel.objects.filter(labelname__exact=labelname)
  if len(res):
    l = res[0]
  else:
    l = models.UserLabel(labelname=labelname)
    l.save()
  user.get_profile().labels.add(l)

def set_defaults():
  """ default values (contents may change with schema) """
  if db_is_installed():
    raise RuntimeError, "Database is already installed."

  # config table defaults
  default_config = (
     ('logging.logfile', 'keg.log'),
     ('logging.logformat', '%(asctime)s %(levelname)-8s (%(name)s) %(message)s'),
     ('logging.use_logfile', 'true'),
     ('logging.use_stream', 'true'),
     ('db.installed', 'true'),
  )
  for key, val in default_config:
    rec = models.Config(key=key, value=val)
    rec.save()

  # KegTap defaults
  main_tap = models.KegTap(name='Main Tap', meter_name='kegboard.flow0')
  main_tap.save()
  secondary_tap = models.KegTap(name='Second Tap', meter_name='kegboard.flow1')
  secondary_tap.save()

  # user defaults
  b = backend.KegbotBackend()
  guest_user = b.CreateNewUser('guest')

  # brewer defaults
  unk_brewer = bdb.Brewer(name='Unknown Brewer')
  unk_brewer.save()

  # beerstyle defaults
  unk_style = bdb.BeerStyle(name='Unknown Style')
  unk_style.save()

  # beertype defaults
  unk_type = bdb.BeerType(name="Unknown Beer", brewer=unk_brewer, style=unk_style)
  unk_type.save()

  # userlabel defaults
  add_label(guest_user, '__default_user__')
  add_label(guest_user, '__no_bac__')

  # KegSize defaults - from http://en.wikipedia.org/wiki/Keg#Size
  default_sizes = (
    (15.5, "Full Keg (half barrel)"),
    (13.2, "Import Keg (European barrel)"),
    (7.75, "Pony Keg (quarter barrel)"),
    (6.6, "European Half Barrel"),
    (5.23, "Sixth Barrel (torpedo keg)"),
    (5.0, "Corny Keg"),
    (1.0, "Mini Keg"),
  )
  for gallons, description in default_sizes:
    volume = units.Quantity(gallons, units.UNITS.USGallon)
    volume_int = volume.Amount(in_units=units.RECORD_UNIT)

    ks = models.KegSize(
      name=description,
      volume_ml=volume_int,
    )
    ks.save()

def gentestdata():
  """ default values (contents may change with schema) """
  sn = bdb.Brewer(name='Sierra Nevada Brewing Company',
        country='USA',
        origin_state='California',
        origin_city='Chico',
        production='commercial',
        url='http://www.sierranevada.com/')
  sn.save()

  an = bdb.Brewer(name='Anchor Brewing Company',
        country='USA',
        origin_state='California',
        origin_city='San Francisco',
        production='commercial',
        url='http://www.anchorsteam.com/')
  an.save()

  # beerstyle defaults
  pale_ale = bdb.BeerStyle(name='Pale Ale')
  pale_ale.save()

  # beertype defaults
  sn_pa = bdb.BeerType(name="Sierra Nevada Pale Ale",
        brewer=sn,
        style=pale_ale,
        calories_oz=10,
        carbs_oz=10,
        abv=5.5)
  sn_pa.save()

  as_pa = bdb.BeerType(name="Anchor Liberty Ale",
        brewer=an,
        style=pale_ale,
        calories_oz=10,
        carbs_oz=10,
        abv=5.0)
  as_pa.save()

  usernames = ['abe', 'bort', 'charlie']
  users = []
  b = backend.KegbotBackend()
  for name in usernames:
    users.append(b.CreateNewUser(name))

  half_barrel = models.KegSize(name="half barrel", volume_ml=10000)
  half_barrel.save()

  k = models.Keg(type=as_pa, size=half_barrel, status='online',
                 origcost=100)
  k.save()

  drink_base = datetime.datetime(2007,1,1,8,0,0)
  drink_interval = datetime.timedelta(seconds=600)
  drink_num = 0
  drink_vols = []
  for ml in (2200, 1100, 550, 715, 780):
    drink_vols.append(units.Quantity(ml, from_units=units.UNITS.KbMeterTick))

  # generate some drinks
  times = (drink_base, drink_base + datetime.timedelta(days=1))

  for drink_time in times:
    for rounds in range(3):
      for u in users:
        start = drink_time + drink_num*drink_interval
        end = start + datetime.timedelta(seconds=10)
        vol = drink_vols[drink_num%len(drink_vols)]
        drink = models.Drink(ticks=vol.ConvertTo.KbMeterTick,
                             volume_ml=vol.Amount(units.RECORD_UNIT),
                             starttime=start, endtime=end, user=u, keg=k,
                             status='valid')
        drink.save()
        drink_num += 1

  # fake thermo data
  thermo_start = datetime.datetime.now() - datetime.timedelta(hours=24)
  sensor_name = "thermo-0000000000000000"
  sensor = models.ThermoSensor.objects.create(raw_name=sensor_name,
      nice_name='Test sensor')
  for minute in xrange(60*24):
    temp_time = thermo_start + datetime.timedelta(minutes=minute)
    slot = (minute + 1)/30.0
    var = math.cos(2 * math.pi * slot)
    temp_value = 5.0 + 2.0*var
    record = models.Thermolog(sensor=sensor, temp=temp_value, time=temp_time)
    record.save()
