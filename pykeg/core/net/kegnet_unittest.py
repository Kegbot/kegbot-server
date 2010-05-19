#!/usr/bin/env python

"""Unittest for kegnet module"""

import asyncore
import logging
import unittest

import gflags

from pykeg.core.net import kegnet

FLAGS = gflags.FLAGS

LOGGER = logging.getLogger('myunittest')

class KegnetTestCase(unittest.TestCase):
  def setUp(self):
    self.server = kegnet.KegnetServer(name='kegnet', kb_env=None,
        addr=FLAGS.kb_core_bind_addr)

  def tearDown(self):
    pass

  def testSimpleFlow(self):
    print 'Starting server'
    self.server.StartServer()
    print 'Done start'
    print 'Looping'
    asyncore.loop(timeout=1, count=1)
    print 'New client'
    client = kegnet.KegnetClient()
    client.SendFlowStart('mytap')
    asyncore.loop(timeout=1, count=1)
    print 'Done'

if __name__ == '__main__':
  import sys
  logging.basicConfig(stream=sys.stderr)
  LOGGER.setLevel(logging.DEBUG)
  LOGGER.info('here i am!')
  unittest.main()
