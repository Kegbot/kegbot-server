"""Miscellaneous protobuf-related utils."""

import datetime


def ProtoMessageToDict(message):
    ret = {}
    # if not message.IsInitialized():
    #  raise ValueError, 'Message not initialized'
    for descriptor, value in message.ListFields():
        if descriptor.is_repeated:
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
            if field.is_required:
                raise ValueError(f"Missing required field {name}")
            continue

        value = values.get(name)
        if field.type == field.TYPE_MESSAGE:
            inner_message = getattr(out_message, name)
            if field.is_repeated:
                for subval in value:
                    DictToProtoMessage(subval, inner_message.add())
            else:
                DictToProtoMessage(value, inner_message)
        else:
            if field.is_repeated:
                out = getattr(out_message, name)
                for v in value:
                    if isinstance(v, datetime.datetime):
                        v = v.isoformat()
                    out.append(v)
            else:
                if isinstance(value, datetime.datetime):
                    value = value.isoformat()
                setattr(out_message, name, value)
    return out_message
