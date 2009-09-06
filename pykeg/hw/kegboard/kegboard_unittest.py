#!/usr/bin/env python

"""Unittest for kegboard module"""

import os
import unittest

from pykeg.hw.kegboard import kegboard

TESTDATA_PATH = os.path.join(os.path.dirname(kegboard.__file__), 'testdata')
CAP_FILE = os.path.join(TESTDATA_PATH, 'one_flow_active.bin')

class MessageTestCase(unittest.TestCase):
  def testMessageCreate(self):
    hello_bytes = kegboard.KBSP_PREFIX + '\x01\x00\x04\x00\x01\x02\x03\x00\x3f\x29'
    m = kegboard.HelloMessage(bytes=hello_bytes)
    self.assertEqual(m.protocol_version.GetValue(), 3)

    m = kegboard.GetMessageForBytes(hello_bytes)
    self.assertEqual(m.protocol_version.GetValue(), 3)
    print m

  def testCapture(self):
    fd = open(CAP_FILE, 'rb')
    messages = []
    for frame in fd.readlines():
      msg = kegboard.GetMessageForBytes(frame[:-2])
      print msg
      messages.append(msg)


class KegboardReaderTestCase(unittest.TestCase):
  def testBasicUse(self):
    fd = open(CAP_FILE, 'rb')
    kbr = kegboard.KegboardReader(fd)

    m = kbr.GetNextMessage()
    self.assert_(isinstance(m, kegboard.HelloMessage))

    m = kbr.GetNextMessage()
    self.assert_(isinstance(m, kegboard.MeterStatusMessage))

    # Next two messages in the cap file are:
    #   METER_STATUS (for flow1)
    #   OUTPUT_STATUS (for output0)
    # Test the framing recovery mechanism by skipping a byte. The mechanism
    # should recover and parse the output0 message.
    fd.read(1)
    m = kbr.GetNextMessage()
    self.assert_(isinstance(m, kegboard.OutputStatusMessage))
    self.assertEqual(m.output_name.GetValue(), "output0")

    print m

  def testAgainstBogusData(self):
    pass

if __name__ == '__main__':
  unittest.main()
