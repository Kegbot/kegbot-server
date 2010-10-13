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

"""Routines from converting data to and from Protocol Buffer format."""

import sys
import time

from pykeg.beerdb import models as bdb_models
from pykeg.core import models

if sys.version_info[:2] < (2, 6):
  import simplejson as json
else:
  import json

_CONVERSION_MAP = {}

class AttrDict(dict):
  def __setattr__(self, name, value):
    self.__setitem__(name, value)

  def __getattr__(self, name):
    try:
      return self.__getitem__(name)
    except KeyError, e:
      raise AttributeError, 'No attribute named %s' % name

def converts(kind):
  def decorate(f):
    global _CONVERSION_MAP
    _CONVERSION_MAP[kind] = f
    return f
  return decorate

def time_to_int(timeval):
  return int(time.mktime(timeval.timetuple()))

def ToProto(obj, full=True):
  """Converts the object to protocol format."""
  if obj is None:
    return None
  kind = obj.__class__
  if hasattr(obj, '__iter__'):
    return (ToProto(item, full) for item in obj)
  elif kind in _CONVERSION_MAP:
    return _CONVERSION_MAP[kind](obj, full)
  else:
    raise ValueError, "Unknown object type: %s" % kind

### Model conversions

@converts(models.AuthenticationToken)
def AuthTokenToProto(record, full=True):
  ret = AttrDict()
  ret.id = '%s|%s' % (record.auth_device, record.token_value)
  ret.auth_device = record.auth_device
  ret.token_value = record.token_value
  if record.user:
    ret.username = record.user.username
    if full:
      ret.user = ToProto(record.user)
  ret.created_time = time_to_int(record.created)
  if record.expires:
    ret.expire_time = time_to_int(record.expires)
  ret.enabled = record.enabled
  if record.pin:
    ret.pin = record.pin
  return ret

@converts(bdb_models.BeerType)
def BeerTypeToProto(beertype, full=True):
  ret = AttrDict()
  ret.id = beertype.id
  ret.name = beertype.name
  ret.brewer_id = beertype.brewer.id
  if full:
    ret.brewer = ToProto(beertype.brewer)
  ret.style_id = beertype.style.id
  if beertype.edition is not None:
    ret.edition = beertype.edition
  if beertype.abv is not None:
    ret.abv = beertype.abv
  if beertype.calories_oz is not None:
    ret.calories_oz = beertype.calories_oz
  if beertype.carbs_oz is not None:
    ret.carbs_oz = beertype.carbs_oz
  return ret

@converts(bdb_models.Brewer)
def BrewerToProto(brewer, full=True):
  ret = AttrDict()
  ret.id = brewer.id
  ret.name = brewer.name
  if brewer.country is not None:
    ret.country = brewer.country
  if brewer.origin_state is not None:
    ret.origin_state = brewer.origin_state
  if brewer.origin_city is not None:
    ret.origin_city = brewer.origin_city
  ret.production = brewer.production
  if brewer.url is not None:
    ret.url = brewer.url
  if brewer.description is not None:
    ret.description = brewer.description
  return ret

@converts(bdb_models.BeerStyle)
def BeerStyleToProto(style, full=True):
  ret = AttrDict()
  ret.id = style.id
  ret.name = style.name
  return ret

@converts(models.Drink)
def DrinkToProto(drink, full=True):
  ret = AttrDict()
  ret.id = drink.seqn
  ret.ticks = drink.ticks
  ret.volume_ml = drink.volume_ml
  ret.session_id = str(drink.session.seqn)
  ret.pour_time = time_to_int(drink.endtime)
  if drink.duration is not None:
    ret.duration = drink.duration
  ret.is_valid = (drink.status == 'valid')
  if drink.keg:
    ret.keg_id = drink.keg.seqn
    if full:
      ret.keg = ToProto(drink.keg)
  if drink.user:
    ret.user_id = drink.user.username
    if full:
      ret.user = ToProto(drink.user)
  if drink.auth_token:
    ret.auth_token = drink.auth_token
  return ret

@converts(models.Keg)
def KegToProto(keg, full=True):
  ret = AttrDict()
  ret.id = keg.seqn
  ret.type_id = keg.type.id
  if full:
    ret.type = ToProto(keg.type)
  ret.size_id = keg.size.id
  rem = float(keg.remaining_volume())
  ret.volume_ml_remain = rem
  ret.percent_full = rem / float(keg.full_volume())
  ret.started_time = time_to_int(keg.startdate)
  ret.finished_time = time_to_int(keg.enddate)
  ret.status = keg.status
  if keg.description:
    ret.description = keg.description
  return ret

@converts(models.KegSize)
def KegSizeToProto(size, full=True):
  ret = AttrDict()
  ret.id = size.id
  ret.name = size.name
  ret.volume_ml = size.volume_ml
  return ret

@converts(models.KegTap)
def KegTapToProto(tap, full=True):
  ret = AttrDict()
  ret.id = str(tap.seqn)
  ret.name = tap.name
  ret.meter_name = tap.meter_name
  ret.ml_per_tick = tap.ml_per_tick
  if tap.description:
    ret.description = tap.description
  if tap.current_keg:
    ret.current_keg_id = tap.current_keg.seqn
    if full:
      ret.current_keg = ToProto(tap.current_keg)
  if tap.temperature_sensor:
    ret.thermo_sensor_id = str(tap.temperature_sensor.seqn)
    if full:
      log = tap.temperature_sensor.LastLog()
      if log:
        ret.last_temperature = ToProto(log)
  return ret

@converts(models.DrinkingSession)
def SessionToProto(record, full=True):
  ret = AttrDict()
  ret.id = str(record.seqn)
  ret.start_time = time_to_int(record.starttime)
  ret.end_time = time_to_int(record.endtime)
  ret.volume_ml = record.volume_ml
  if full:
    ret.drinks = []
    for d in drinks:
      out_d.append(ToProto(d, full))
  return ret

@converts(models.Thermolog)
def ThermoLogToProto(record, full=True):
  ret = AttrDict()
  ret.id = str(record.seqn)
  ret.sensor_id = str(record.sensor.seqn)
  ret.temperature_c = record.temp
  ret.record_time = time_to_int(record.time)
  return ret

@converts(models.ThermoSensor)
def ThermoSensorToProto(record, full=True):
  ret = AttrDict()
  ret.sensor_name = record.raw_name
  ret.nice_name = record.nice_name
  return ret

@converts(models.User)
def UserToProto(user, full=True):
  ret = AttrDict()
  ret.username = user.username
  ret.mugshot_url = user.get_profile().MugshotUrl()
  ret.is_active = user.is_active
  ret.is_staff = user.is_staff
  ret.is_superuser = user.is_superuser
  ret.joined_time = time_to_int(user.date_joined)
  return ret

@converts(models.SessionChunk)
def SessionChunkToProto(record, full=True):
  ret = AttrDict()
  ret.id = str(record.seqn)
  ret.session_id = str(record.session.seqn)
  ret.username = record.user.username
  ret.keg_id = record.keg.seqn
  ret.start_time = time_to_int(record.starttime)
  ret.end_time = time_to_int(record.endtime)
  ret.volume_ml = record.volume_ml
  return ret

