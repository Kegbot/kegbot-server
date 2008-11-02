#!/usr/bin/env python

"""Unittest for kegbot module"""

import commands
import time
import logging
import socket
import unittest
import kegbot

from django.test import TestCase

from pykeg.core import defaults
from pykeg.core import models
from pykeg.core import kb_common
from pykeg.scripts import gentestdata

class KegbotTestCase(TestCase):
  def setUp(self):
    defaults.set_defaults()
    gentestdata.set_data()
    self.kegbot = kegbot.KegBot(daemon=False)
    self.kegbot._StartThreads()

  def tearDown(self):
    for thr in self.kegbot._threads:
      self.assert_(thr.isAlive(), "thread %s died unexpectedly" % thr.getName())
    self.kegbot.Quit()
    for thr in self.kegbot._threads:
      self.assert_(not thr.isAlive(), "thread %s stuck" % thr.getName())
    del self.kegbot

  def testApplication(self):
    # This test is really exercising the setUp and tearDown routines, which
    # should take care of cleaning up everything for subsequent tests
    for i in xrange(100):
      self.kegbot._StepEventLoop()

  def testSimpleFlow(self):
    # WTF? Django test db does not work with multiple threads. Move drink
    # processing to main thread with this little hack.
    self.kegbot._flow_thread.QueueFlow = self.kegbot._flow_thread._ProcessFlow

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))

    for x in xrange(100):
      self.kegbot._StepEventLoop()

    # Send two packets to the network flow client
    msg1 = 'netboard - flow:1:0\n'
    sock.sendto(msg1, ('224.107.101.103', 9012))
    msg2 = 'netboard - flow:1:2200\n'
    sock.sendto(msg2, ('224.107.101.103', 9012))

    for x in xrange(100):
      self.kegbot._StepEventLoop()

    # Idle out the flow. This is a hack.
    f = self.kegbot._GetFlowForChannel(self.kegbot._channel_0)
    f._last_activity = time.time() - 60

    for x in xrange(100):
      self.kegbot._StepEventLoop()

    drinks = models.Drink.objects.all().order_by('-id')
    last_drink = drinks[0]

    print 'last drink:', last_drink
    self.assertEquals(last_drink.ticks, 2200)

  def testOther(self):
    return True

if __name__ == '__main__':
  unittest.main()
