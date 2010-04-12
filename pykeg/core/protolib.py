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

from pykeg.core import models
from pykeg.core import models_pb2

if sys.version_info[:2] < (2, 6):
  import simplejson as json
else:
  import json

_CONVERSION_MAP = {}

def converts(kind):
  def decorate(f):
    global _CONVERSION_MAP
    _CONVERSION_MAP[kind] = f
    return f
  return decorate

def time_to_int(timeval):
  return int(time.mktime(timeval.timetuple()))

def ToProto(obj, full=True):
  """Converts the object to protocol buffer format.

  `obj` may be of any object with a protobuf equivalent.
  """
  kind = obj.__class__
  if kind in _CONVERSION_MAP:
    return _CONVERSION_MAP[kind](obj, full)
  raise ValueError, "Unknown object type: %s" % kind

def ProtoMessageToDict(message):
  ret = {}
  if not message.IsInitialized():
    raise ValueError, 'Message not initialized'
  for descriptor, value in message.ListFields():
    if descriptor.type == descriptor.TYPE_MESSAGE:
      ret[descriptor.name] = ProtoMessageToDict(value)
    else:
      ret[descriptor.name] = value
  return ret

def DictToProtoMessage(values, out_message):
  for name, field in out_message.DESCRIPTOR.fields_by_name.iteritems():
    if name not in values:
      if field.label == field.LABEL_REQUIRED:
        raise ValueError, "Missing required field %s" % name
      continue

    value = values.get(name)
    if field.type == field.TYPE_MESSAGE:
      inner_message = gettattr(out_message, name)
      value = FromDict(inner_message, value)
    setattr(out_message, name, value)
  return out_message

### Model conversions

@converts(models.Keg)
def KegToProto(keg, full=True):
  ret = models_pb2.Keg()
  ret.id = keg.id
  ret.type_id = keg.type.id
  if full:
    ret.type.CopyFrom(ToProto(keg.type))
  ret.size_id = keg.size.id
  if full:
    ret.size.CopyFrom(ToProto(keg.size))
  ret.startdate = time_to_int(keg.startdate)
  ret.enddate = time_to_int(keg.enddate)
  if keg.description:
    ret.description = keg.description
  if keg.origcost is not None:
    ret.origcost = keg.origcost
  return ret

@converts(models.BeerType)
def BeerTypeToProto(beertype, full=True):
  ret = models_pb2.BeerType()
  ret.id = beertype.id
  ret.name = beertype.name
  ret.brewer_id = beertype.brewer.id
  if full:
    ret.brewer.CopyFrom(ToProto(beertype.brewer))
  ret.style_id = beertype.style.id
  if full:
    ret.style.CopyFrom(ToProto(beertype.style))
  ret.calories_oz = beertype.calories_oz
  ret.carbs_oz = beertype.carbs_oz
  ret.abv = beertype.abv
  return ret

@converts(models.Brewer)
def BrewerToProto(brewer, full=True):
  ret = models_pb2.Brewer()
  ret.id = brewer.id
  ret.name = brewer.name
  ret.origin_country = brewer.origin_country
  ret.origin_state = brewer.origin_state
  if brewer.origin_city is not None:
    ret.origin_city = brewer.origin_city
  ret.distribution = brewer.distribution
  return ret

@converts(models.BeerStyle)
def BeerStyleToProto(style, full=True):
  ret = models_pb2.BeerStyle()
  ret.id = style.id
  ret.name = style.name
  return ret

@converts(models.Drink)
def DrinkToProto(drink, full=True):
  ret = models_pb2.Drink()
  ret.id = drink.id
  ret.ticks = drink.ticks
  ret.volume_ml = drink.volume_ml
  ret.starttime = time_to_int(drink.starttime)
  ret.endtime = time_to_int(drink.endtime)
  ret.is_valid = (drink.status == 'valid')
  if drink.keg:
    ret.keg_id = drink.keg.id
    if full:
      ret.keg.CopyFrom(ToProto(drink.keg))
  ret.user_id = drink.user.username
  if full:
    ret.user.CopyFrom(ToProto(drink.user))
  return ret

@converts(models.User)
def UserToProto(user, full=True):
  ret = models_pb2.User()
  ret.username = user.username
  #ret.mugshot_url = ''
  ret.is_active = user.is_active
  ret.is_unknown = user.get_profile().HasLabel('__default_user__')
  ret.is_staff = user.is_staff
  ret.is_superuser = user.is_superuser
  ret.date_joined = time_to_int(user.date_joined)
  return ret

@converts(models.KegTap)
def KegTapToProto(tap, full=True):
  ret = models_pb2.KegTap()
  ret.id = tap.id
  ret.name = tap.name
  if tap.description:
    ret.description = tap.description
  if tap.current_keg:
    ret.current_keg_id = tap.current_keg.id
    if full:
      ret.current_keg.CopyFrom(ToProto(tap.current_keg))
  return ret

@converts(models.KegSize)
def KegSizeToProto(size, full=True):
  ret = models_pb2.KegSize()
  ret.id = size.id
  ret.name = size.name
  ret.volume_ml = size.volume_ml
  return ret
