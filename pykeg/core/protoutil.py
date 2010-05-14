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

import sys

if sys.version_info[:2] < (2, 6):
  import simplejson as json
else:
  import json

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
      value = DictToProtoMessage(inner_message, value)
    setattr(out_message, name, value)
  return out_message

