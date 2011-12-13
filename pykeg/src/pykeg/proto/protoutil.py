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

"""Miscellaneous protobuf-related utils."""

import datetime

from pykeg.core import util

try:
  from django.conf import settings
  TIME_ZONE = settings.TIME_ZONE
except ImportError:
  TIME_ZONE = 'America/Los_Angeles'

def ProtoMessageToDict(message):
  ret = util.AttrDict()
  #if not message.IsInitialized():
  #  raise ValueError, 'Message not initialized'
  for descriptor, value in message.ListFields():
    if descriptor.label == descriptor.LABEL_REPEATED:
      if descriptor.type == descriptor.TYPE_MESSAGE:
        ret[descriptor.name] = [ProtoMessageToDict(v) for v in value]
      else:
        ret[descriptor.name] = [v for v in value]
    else:
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
      inner_message = getattr(out_message, name)
      if field.label == field.LABEL_REPEATED:
        for subval in value:
          DictToProtoMessage(subval, inner_message.add())
      else:
        DictToProtoMessage(value, inner_message)
    else:
      if field.label == field.LABEL_REPEATED:
        out = getattr(out_message, name)
        for v in value:
          if isinstance(v, datetime.datetime):
            v = util.datetime_to_iso8601str(v, TIME_ZONE)
          out.append(v)
      else:
        if isinstance(value, datetime.datetime):
          value = util.datetime_to_iso8601str(value, TIME_ZONE)
        setattr(out_message, name, value)
  return out_message

