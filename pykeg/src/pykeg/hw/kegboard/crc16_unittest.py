#!/usr/bin/env python

"""Unittest for crc16 module."""

import struct
import unittest

from pykeg.hw.kegboard import crc16

class CrcTestCase(unittest.TestCase):
  def testCrc(self):
    data = '\x01\x02\x03\x04'
    crc = crc16.crc16_ccitt(data)
    data += struct.pack('<H', crc)
    self.assertEqual(crc16.crc16_ccitt(data), 0)
