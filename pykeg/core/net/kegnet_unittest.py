#!/usr/bin/env python

"""Unittest for kegnet module"""

import unittest
from pykeg.core.net import kegnet
from pykeg.core.net import net
from pykeg.core.net.proto import kegnet_pb2

class ClientServerTestCase(unittest.TestCase):
  def setUp(self):
    self._thr = net.PumpThread('pump')
    self._thr.start()

  def tearDown(self):
    self._thr.Quit()

  def testBasicUse(self):
    # TODO(mikey): mock kb_env
    pass


if __name__ == '__main__':
  unittest.main()
