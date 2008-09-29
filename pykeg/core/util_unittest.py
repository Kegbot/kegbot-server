#!/usr/bin/env python

"""Unittest for util module"""

import unittest
import util

class EnumTestCase(unittest.TestCase):
  def setUp(self):
    self.enum = util.Enum(*(
      'Foo',
      'Bar',
      'Baz',
    ))

  def testBasicUse(self):
    self.assertNotEqual(self.enum.Foo, self.enum.Bar)
    self.assertEqual(str(self.enum.Bar), 'Bar')

class SimpleGraphTestCase(unittest.TestCase):
  def setUp(self):
    self.graph = util.SimpleGraph((
        ('a', 'b'),
        ('a', 'c'),
        ('c', 'd'),
        ('d', 'e'),
        ('c', 'e'),
        ('e', 'f'),
    ))

  def testReverseMappings(self):
    self.assertEquals(['a', 'c'], self.graph.ShortestPath('a', 'c'))
    self.assertEquals(['a', 'c', 'e', 'f'], self.graph.ShortestPath('a', 'f'))

if __name__ == '__main__':
  unittest.main()
