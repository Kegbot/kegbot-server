"""Module for common handling of JSON within Kegbot.

This module's 'loads' and 'dumps' implementations add support for encoding
datetime instances to ISO8601 strings, and decoding them back.
"""

import datetime
import isodate
import types
import json
from addict import Dict


class JSONEncoder(json.JSONEncoder):
    """JSONEncoder which translate datetime instances to ISO8601 strings."""

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return isodate.datetime_isoformat(obj)
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
    if type(obj) == dict:
        # Try to convert any "time" or "date" fields into datetime objects.  If the
        # format doesn't match, just leave it alone.
        for k, v in list(obj.items()):
            if type(v) in (str,):
                if (
                    k.endswith("date")
                    or k.endswith("time")
                    or k.startswith("date")
                    or k.startswith("last_login")
                ):
                    try:
                        obj[k] = isodate.parse_datetime(v)
                    except ValueError:
                        pass
        return Dict(obj)
    return obj


def loads(data):
    return json.loads(data, object_hook=_ToAttrDict)


def dumps(obj, indent=2, cls=JSONEncoder):
    return json.dumps(obj, indent=indent, cls=cls)
