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
datetime instances to ISO8601 strings.
"""

import datetime
import types

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


class JSONEncoder(json.JSONEncoder):
  """JSONEncoder which translate datetime instances to ISO8601 strings."""
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    return json.JSONEncoder.default(self, obj)


def _ToAttrDict(obj):
  """JSONDecoder object_hook that translates dicts to AttrDicts."""
  if type(obj) == types.DictType:
    return AttrDict(obj)
  return obj


def loads(data):
  return json.loads(data, object_hook=_ToAttrDict)

def dumps(obj, indent=2, cls=JSONEncoder):
  return json.dumps(obj, indent=indent, cls=cls)
