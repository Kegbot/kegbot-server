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

"""Module for common handling of JSON within Kegbot.

This module's 'loads' and 'dumps' implementations add support for encoding
datetime instances to ISO8601 strings, and decoding them back.
"""

import datetime
import pytz
import re
import types

from django.conf import settings
from pykeg.core.util import AttrDict

try:
  import json
except ImportError:
  try:
    import simplejson as json
  except ImportError:
    try:
      from django.utils import simplejson as json
    except ImportError:
      raise ImportError, "Unable to load a json library"

def _tzswap(dt, tz_from, tz_to):
  """Reinterprets a datetime object produced with one timezone with another.

  The input and output are both naieve datetimes, that is, those without any
  tzinfo.
  """
  assert dt.tzinfo == None
  # First, reinterpret the source datetime obj as being in the 'from' timezone.
  res = dt.replace(tzinfo=tz_from)
  # Next, update with the intended timezone.
  res = res.astimezone(tz_to)
  # Finally, strip away the new timezone to leave us with a naieve datetime once
  # again.
  res = res.replace(tzinfo=None)
  return res

def utc_to_local(dt):
  local_tz = pytz.timezone(settings.TIME_ZONE)
  utc_tz = pytz.timezone('UTC')
  return _tzswap(dt, utc_tz, local_tz)

def local_to_utc(dt):
  local_tz = pytz.timezone(settings.TIME_ZONE)
  utc_tz = pytz.timezone('UTC')
  return _tzswap(dt, local_tz, utc_tz)

class JSONEncoder(json.JSONEncoder):
  """JSONEncoder which translate datetime instances to ISO8601 strings."""
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      try:
        # Convert from local to UTC.
        # TODO(mikey): handle incoming datetimes with tzinfo.
        obj = local_to_utc(obj)
      except pytz.UnknownTimeZoneError:
        pass
      return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    return json.JSONEncoder.default(self, obj)


def _ToAttrDict(obj):
  """JSONDecoder object_hook that translates dicts and ISO times.

  Dictionaries are converted to AttrDicts, which allow element access by
  attribute (getattr).

  Also, an attempt will be made to convert any field ending in 'date' or 'time'
  to a datetime.datetime object.  The format is expected to match the ISO8601
  format used in JSONEncoder.  If it does not parse, the value will be left as a
  string.
  """
  if type(obj) == types.DictType:
    # Try to convert any "time" or "date" fields into datetime objects.  If the
    # format doesn't match, just leave it alone.
    for k, v in obj.iteritems():
      if k.endswith('date') or k.endswith('time') or k.startswith('date') or k.startswith('last_login'):
        try:
          timeval = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ')
          # Convert from UTC to local.
          try:
            timeval = utc_to_local(timeval)
          except pytz.UnknownTimeZoneError:
            pass
          obj[k] = timeval
        except ValueError:
          pass
    return AttrDict(obj)
  return obj


def loads(data):
  return json.loads(data, object_hook=_ToAttrDict)

def dumps(obj, indent=2, cls=JSONEncoder):
  return json.dumps(obj, indent=indent, cls=cls)
