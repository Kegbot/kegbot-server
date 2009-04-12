#!/usr/bin/env python

"""Unittest for kegnet module"""

import unittest
from pykeg.core.net import kegnet
from pykeg.core.net.proto import kegnet_pb2

class ProtobufTestCase(unittest.TestCase):
  def testSerialization(self):
    msg = kegnet_pb2.FlowUpdate()
    msg.name = "mymeter"
    msg.count = 12345
    bytes = msg.SerializeToString()

    wire_msg = kegnet.msg_to_wire_msg(msg)
    wire_bytes = wire_msg.SerializeToString()

    unpacked_msg = kegnet.msg_from_wire_bytes(wire_bytes)

    print unpacked_msg
    self.assertEqual(msg, unpacked_msg)


if __name__ == '__main__':
  unittest.main()
