# Copyright 2008 Mike Wakerly <opensource@hoho.com>
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

"""Kegnet protocol library.

The module wraps the protocol-buffer implementation of the kegnet communication
protocol.
"""

from google.protobuf.message import Message as protobuf_Message
from pykeg.core.net.proto import kegnet_pb2


# This map must be kept in sync with the constants defined in kegnet.proto
__ids = kegnet_pb2.WireMessage
ID_TO_MESSAGE = {
  ### Core messages
  __ids.CLIENT_CONNECT : kegnet_pb2.ClientConnect,
  __ids.CLIENT_DISCONNECT: kegnet_pb2.ClientDisconnect,
  __ids.STATUS_REPLY : kegnet_pb2.StatusReply,
  __ids.PING_REQUEST : kegnet_pb2.PingRequest,
  __ids.PING_REPLY : kegnet_pb2.PingReply,

  ### Flow messages
  __ids.REGISTER_FLOW_DEV : kegnet_pb2.RegisterFlowDev,
  __ids.UNREGISTER_FLOW_DEV : kegnet_pb2.UnregisterFlowDev,
  __ids.FLOW_UPDATE : kegnet_pb2.FlowUpdate,
  __ids.FLOW_END : kegnet_pb2.FlowEnd,

  ### Thermo messages
  __ids.THERMO_STATUS : kegnet_pb2.ThermoStatus,

  ### Output messages
  __ids.OUTPUT_STATUS : kegnet_pb2.OutputStatus,
}

MESSAGE_TO_ID = dict((v, k) for (k, v) in ID_TO_MESSAGE.iteritems())

class KegnetError(Exception):
  """Generic error for kegnet module."""


class UnknownMessageError(Exception):
  """Message type or ID is not known."""


# TODO(mikey): This class only exists to provide kwargs-based instatiation of
# protobuf message objects. There must be a better way.

class Message:

  @classmethod
  def ClientConnect(cls, client_name):
    msg = kegnet_pb2.ClientConnect()
    msg.client_name = client_name
    return msg

  @classmethod
  def ClientDisconnect(cls, client_name):
    msg = kegnet_pb2.ClientDisonnect()
    msg.client_name = client_name
    return msg

  @classmethod
  def RegisterFlowDev(cls, name):
    msg = kegnet_pb2.RegisterFlowDev()
    msg.name = name
    return msg

  @classmethod
  def FlowUpdate(cls, name, count):
    msg = kegnet_pb2.FlowUpdate()
    msg.name = name
    msg.count = count
    return msg

  @classmethod
  def FlowEnd(cls, name):
    msg = kegnet_pb2.FlowEnd()
    msg.name = name
    return msg

  @classmethod
  def ThermoStatus(cls, name, reading):
    msg = kegnet_pb2.ThermoStatus()
    msg.name = name
    msg.reading = reading
    return msg

  @classmethod
  def OutputStatus(cls, name, on):
    msg = kegnet_pb2.OutputStatus()
    msg.name = name
    if on:
      msg.status = msg.ENABLED
    else:
      msg.status = msg.DISABLED
    return msg

  @classmethod
  def StatusReply(cls, code, description=''):
    msg = kegnet_pb2.StatusReply()
    msg.code = code
    if description:
      msg.description = description
    return msg


class GenericResponse:
  """Static canned reply messages."""

  OK = Message.StatusReply(code=kegnet_pb2.StatusReply.OK)
  ALREADY_EXISTS = Message.StatusReply(code=kegnet_pb2.StatusReply.ERROR)
  UNKNOWN_FAILURE = Message.StatusReply(code=kegnet_pb2.StatusReply.ERROR)


def msg_to_wire_msg(msg):
  """Convert a message to wire format, and return wire message."""
  assert isinstance(msg, protobuf_Message)
  msg_id = MESSAGE_TO_ID.get(msg.__class__)
  if msg_id is None:
    raise UnknownMessageError, "ID for message class not found"
  msg_bytes = msg.SerializeToString()

  wire_msg = kegnet_pb2.WireMessage()
  wire_msg.message_type = msg_id
  wire_msg.data = msg_bytes
  wire_msg.message_length = wire_msg.ByteSize()
  return wire_msg

def msg_to_wire_bytes(msg):
  """Convert a message to wire format, and return raw bytes."""
  return msg_to_wire_msg(msg).SerializeToString()

def msg_from_wire_msg(wire_msg):
  """Get the inner message from a wire message."""
  assert isinstance(wire_msg, kegnet_pb2.WireMessage)
  msg_cls = ID_TO_MESSAGE.get(wire_msg.message_type)
  if msg_cls is None:
    raise UnknownMessageError, "Class for message ID not found"

  msg = msg_cls()
  msg.ParseFromString(wire_msg.data)
  return msg

def wire_msg_from_bytes(bytes):
  """Get a wire message from a wire message bytestream."""
  wire_msg = kegnet_pb2.WireMessage()
  wire_msg.ParseFromString(bytes)
  return wire_msg

def msg_from_wire_bytes(bytes):
  """Get the inner message from a wire message bytestream."""
  return msg_from_wire_msg(wire_msg_from_bytes(bytes))

