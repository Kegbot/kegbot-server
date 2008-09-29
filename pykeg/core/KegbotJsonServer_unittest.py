#!/usr/bin/env python

"""Unittest for KegbotJsonServer module"""

import time
import unittest

from pykeg.core import KegbotJsonServer

TEST_PORT = 8899

class ServerTestCase(unittest.TestCase):
  def setUp(self):
    self.server = KegbotJsonServer.KegbotJsonServer(('', TEST_PORT))
    self.server.start()

  def tearDown(self):
    self.server.Quit()
    self.server.join()

  def testServer(self):
    time.sleep(3)
    # TODO: expand me


if __name__ == '__main__':
  unittest.main()
