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
from pykeg.core.util import AttrDict

_CONVERSION_MAP = {}

def converts(kind):
  def decorate(f):
    global _CONVERSION_MAP
    _CONVERSION_MAP[kind] = f
    return f
  return decorate

def ToProto(obj):
  """Converts the object to protocol format."""
  if obj is None:
    return None
  kind = obj.__class__
  if hasattr(obj, '__iter__'):
    return (ToProto(item) for item in obj)
  elif kind in _CONVERSION_MAP:
    return _CONVERSION_MAP[kind](obj)
  else:
    raise ValueError, "Unknown object type: %s" % kind

### Model conversions

@converts(models.AuthenticationToken)
def AuthTokenToProto(record):
  ret = AttrDict()
  ret.id = '%s|%s' % (record.auth_device, record.token_value)
  ret.auth_device = record.auth_device
  ret.token_value = record.token_value
  if record.user:
    ret.username = str(record.user.username)
  else:
    ret.username = None
  ret.created_time = record.created
  if record.expires:
    ret.expire_time = record.expires
  ret.enabled = record.enabled
  if record.pin:
    ret.pin = record.pin
  return ret

@converts(bdb_models.BeerType)
def BeerTypeToProto(beertype):
  ret = AttrDict()
  ret.id = beertype.id
  ret.name = beertype.name
  ret.brewer_id = beertype.brewer.id
  ret.style_id = beertype.style.id
  ret.style = beertype.style.name
  if beertype.edition is not None:
    ret.edition = beertype.edition
  if beertype.abv is not None:
    ret.abv = beertype.abv
  if beertype.calories_oz is not None:
    ret.calories_oz = beertype.calories_oz
  if beertype.carbs_oz is not None:
    ret.carbs_oz = beertype.carbs_oz
  ret.brewer = ToProto(beertype.brewer)
  return ret

@converts(bdb_models.Brewer)
def BrewerToProto(brewer):
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
def BeerStyleToProto(style):
  ret = AttrDict()
  ret.id = style.id
  ret.name = style.name
  return ret

@converts(models.Drink)
def DrinkToProto(drink):
  ret = AttrDict()
  ret.id = drink.seqn
  ret.ticks = drink.ticks
  ret.volume_ml = drink.volume_ml
  ret.session_id = str(drink.session.seqn)
  ret.pour_time = drink.endtime
  if drink.duration is not None:
    ret.duration = drink.duration
  ret.is_valid = (drink.status == 'valid')
  if drink.keg:
    ret.keg_id = drink.keg.seqn
  if drink.user:
    ret.user_id = drink.user.username
  else:
    ret.user_id = None
    ret.user = None
  if drink.auth_token:
    ret.auth_token = drink.auth_token
  return ret

@converts(models.Keg)
def KegToProto(keg):
  ret = AttrDict()
  ret.id = keg.seqn
  ret.type_id = keg.type.id
  ret.size_id = keg.size.id
  rem = float(keg.remaining_volume())
  ret.volume_ml_remain = rem
  ret.percent_full = rem / float(keg.full_volume())
  ret.started_time = keg.startdate
  ret.finished_time = keg.enddate
  ret.status = keg.status
  if keg.description:
    ret.description = keg.description
  return ret

@converts(models.KegSize)
def KegSizeToProto(size):
  ret = AttrDict()
  ret.id = size.id
  ret.name = size.name
  ret.volume_ml = size.volume_ml
  return ret

@converts(models.KegTap)
def KegTapToProto(tap):
  ret = AttrDict()
  ret.id = str(tap.seqn)
  ret.name = tap.name
  ret.meter_name = tap.meter_name
  ret.ml_per_tick = tap.ml_per_tick
  if tap.description:
    ret.description = tap.description
  if tap.current_keg:
    ret.current_keg_id = tap.current_keg.seqn
  if tap.temperature_sensor:
    ret.thermo_sensor_id = str(tap.temperature_sensor.seqn)
    log = tap.temperature_sensor.LastLog()
    if log:
      ret.last_temperature = ToProto(log)
    else:
      ret.last_temperature = None
  return ret

@converts(models.DrinkingSession)
def SessionToProto(record):
  ret = AttrDict()
  ret.id = str(record.seqn)
  ret.start_time = record.starttime
  ret.end_time = record.endtime
  ret.volume_ml = record.volume_ml
  return ret

@converts(models.Thermolog)
def ThermoLogToProto(record):
  ret = AttrDict()
  ret.id = str(record.seqn)
  ret.sensor_id = str(record.sensor.seqn)
  ret.temperature_c = record.temp
  ret.record_time = record.time
  return ret

@converts(models.ThermoSensor)
def ThermoSensorToProto(record):
  ret = AttrDict()
  ret.sensor_name = record.raw_name
  ret.nice_name = record.nice_name
  return ret

@converts(models.User)
def UserToProto(user):
  ret = AttrDict()
  ret.username = user.username
  ret.mugshot_url = user.get_profile().MugshotUrl()
  ret.is_active = user.is_active
  ret.is_staff = user.is_staff
  ret.is_superuser = user.is_superuser
  ret.joined_time = user.date_joined
  return ret

@converts(models.SessionChunk)
def SessionChunkToProto(record):
  ret = AttrDict()
  ret.id = str(record.seqn)
  ret.session_id = str(record.session.seqn)
  ret.username = record.user.username
  ret.keg_id = record.keg.seqn
  ret.start_time = record.starttime
  ret.end_time = record.endtime
  ret.volume_ml = record.volume_ml
  return ret

