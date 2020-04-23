#!/usr/bin/env python

"""Unittest for units module"""
from __future__ import absolute_import

import unittest
from . import units

UNITS = units.UNITS


class QuantityTestCase(unittest.TestCase):
    def testSameUnits(self):
        amt = 123.45
        for unit_type in UNITS:
            v = units.Quantity(amt, unit_type).ConvertTo(unit_type)
            self.assertEqual(v.Amount(), 123.45)

    def testSimpleConversion(self):
        self.assertAlmostEqual(16, units.Quantity(1, UNITS.Pint, UNITS.Ounce).Amount())
        self.assertAlmostEqual(8, units.Quantity(1, UNITS.USGallon, UNITS.Pint).Amount(), places=6)
        self.assertNotEqual(1.0, units.Quantity(1, UNITS.Liter, UNITS.Pint).Amount())

        self.assertEqual(4, units.Quantity(4000, UNITS.Milliliter, UNITS.Liter).Amount())
        self.assertEqual(1.234, units.Quantity(1234, UNITS.Milliliter, UNITS.Liter).Amount())

        amt_liter = 1234.56
        amt_gal = units.Quantity(amt_liter, UNITS.Liter, UNITS.USGallon)
        self.assertEqual(amt_liter, units.Quantity(amt_gal, UNITS.USGallon, UNITS.Liter).Amount())

    def testBasicUsage(self):
        v = units.Quantity(1234.0)
        self.assertEqual(1.234, v.InLiters())

        v = v + units.Quantity(1, UNITS.Liter)
        self.assertEqual(2.234, v.InLiters())

        v = units.Quantity(0)
        self.assertEqual(0, v.InLiters())

        v = units.Quantity(256, UNITS.Ounce)
        self.assertAlmostEqual(2.0, v.InUSGallons())

        v = v + units.Quantity(-0.5, UNITS.USGallon)
        self.assertAlmostEqual(1.5, v.InUSGallons())

        v1 = units.Quantity(123.0)
        v2 = units.Quantity(123)
        self.assertEqual(v1, v2)

    def testOpers(self):
        v1 = units.Quantity(330, UNITS.Milliliter)
        v2 = units.Quantity(1.5, UNITS.Liter)

        # add quantities should work
        res = v1 + v2
        self.assertAlmostEqual(res.Amount(), units.Quantity(1.830, UNITS.Liter).InMilliliters())

        # adding int types works like adding same quantity
        res = v1 + 100
        self.assertEqual(res.Amount(), units.Quantity(0.430, UNITS.Liter).InMilliliters())

        # test subtraction
        v3 = v2 - v1
        self.assertEqual(v3.InMilliliters(), units.Quantity(1170, UNITS.Milliliter).InMilliliters())


if __name__ == "__main__":
    unittest.main()
