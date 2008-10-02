#!/usr/bin/env python

"""Unittest for Net module"""

import unittest
import time
import socket

from pykeg.core import models
from pykeg.core.Devices import Net

class NetAuthTestCase(unittest.TestCase):
  def testProtocol(self):
    thr = Net.NetAuth()

    tok1_str = "0011223344556677"
    tok2_str = "2222222222222222"
    test_user_1 = models.User.objects.create(username="id_test_1")
    tok1 = models.Token.objects.create(user=test_user_1, keyinfo=tok1_str)
    test_user_2 = models.User.objects.create(username="id_test_2")
    tok2 = models.Token.objects.create(user=test_user_2, keyinfo=tok2_str)

    pkt = "0x%s 0x%s foobar\n" % (tok1_str, tok2_str)
    thr._HandlePacket(pkt)

    self.assertEquals(thr.AuthorizedUsers(), set([u'id_test_1', u'id_test_2']))


if __name__ == '__main__':
  unittest.main()
