"""Miscellaneous protobuf-related utils."""

from future.utils import raise_
import datetime

TIME_ZONE = 'UTC'

def ProtoMessageToDict(message):
  ret = {}
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
  for name, field in out_message.DESCRIPTOR.fields_by_name.items():
    if name not in values:
      if field.label == field.LABEL_REQUIRED:
        raise_(ValueError, "Missing required field %s" % name)
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

