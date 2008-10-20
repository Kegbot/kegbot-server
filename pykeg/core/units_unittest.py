#!/usr/bin/env python

"""Unittest for units module"""

import unittest
import units

UNITS = units.UNITS

class UnitsTestCase(unittest.TestCase):
  def testReverseMappings(self):
    converter = units.UnitConverter

    # ensure reverse mappings are in place
    for k, orig_val in converter._table.iteritems():
      from_unit, to_unit = k
      reverse_key = (to_unit, from_unit)
      self.assert_(converter.CanConvert(*reverse_key),
                   "reverse for %s not found" % str(k))

      reverse_val = converter._table[reverse_key]
      computed_reverse_val = 1.0/orig_val
      delta = abs(reverse_val - computed_reverse_val)
      # Not using assertAlmostEqual: can we reliably predict the right value of
      # "places"?
      self.assert_(delta < .000001)

  def testSameUnits(self):
    converter = units.UnitConverter
    amt = 123.45
    for unit_type in UNITS:
      self.assertEqual(amt, converter.Convert(amt, unit_type, unit_type))

  def testSimpleConversion(self):
    converter = units.UnitConverter

    self.assertEqual(16, converter.Convert(1, UNITS.Pint, UNITS.Ounce))
    self.assertEqual(8, converter.Convert(1, UNITS.USGallon, UNITS.Pint))
    self.assertNotEqual(1.0, converter.Convert(1, UNITS.Liter, UNITS.Pint))

    self.assertEqual(4, converter.Convert(4000, UNITS.Milliliter, UNITS.Liter))
    self.assertEqual(1.234, converter.Convert(1234, UNITS.Milliliter, UNITS.Liter))

    amt_liter = 1234.56
    amt_gal = converter.Convert(amt_liter, UNITS.Liter, UNITS.USGallon)
    self.assertEqual(amt_liter, converter.Convert(amt_gal, UNITS.USGallon,
                                                  UNITS.Liter))

  def testPartialTable(self):
    """Test a conversion table lacking closure on all units"""
    # fake enum vals
    FOO_UNIT, BAR_UNIT, WEEK_UNIT, DAY_UNIT = (1, 2, 3, 4)
    table = {
        (FOO_UNIT, BAR_UNIT) : 2,  # FOO is twice the size of BAR
        (WEEK_UNIT, DAY_UNIT) : 7.0, # 7 days in a week,
    }
    converter = units._UnitConverter(table)

    # we can convert foos to bars easily
    self.assertEqual(3.0, converter.Convert(1.5, FOO_UNIT, BAR_UNIT))
    self.assertEqual(1.0, converter.Convert(2.0, BAR_UNIT, FOO_UNIT))

    # and days to weeks
    self.assertEqual(14.0, converter.Convert(2.0, WEEK_UNIT, DAY_UNIT))
    self.assertEqual(5.0, converter.Convert(35, DAY_UNIT, WEEK_UNIT))

    # but there's no way to convert BARs to WEEKs
    self.assertRaises(units.ConversionError, converter.Convert, 1.0, BAR_UNIT,
                      WEEK_UNIT)

class QuantityTestCase(unittest.TestCase):
  """Test the units.Quantity class"""
  def testBasicUsage(self):
    v = units.Quantity(1234.0)
    self.assertEqual(1.234, v.ConvertTo.Liter)

    v.IncAmount(1, UNITS.Liter)
    self.assertEqual(2.234, v.ConvertTo.Liter)

    v.Clear()
    self.assertEqual(0, v.ConvertTo.Liter)

    v.SetAmount(256, UNITS.Ounce)
    self.assertEqual(2.0, v.ConvertTo.USGallon)

    v.IncAmount(-0.5, UNITS.USGallon)
    self.assertEqual(1.5, v.ConvertTo.USGallon)

    v1 = units.Quantity(123.0)
    v2 = units.Quantity(123, from_units=units.Quantity.DEFAULT_UNITS)
    self.assertEqual(v1, v2)

  def testOpers(self):
    v1 = units.Quantity(330, UNITS.Milliliter)
    v2 = units.Quantity(1.5, UNITS.Liter)

    # add quantities should work
    res = v1 + v2
    self.assertEqual(res, units.Quantity(1.830, UNITS.Liter))

    # adding int types works like adding same quantity
    res = v1 + 100
    self.assertEqual(res, units.Quantity(0.430, UNITS.Liter))

    # test subtraction
    v3 = v2 - v1
    self.assertEqual(v3, units.Quantity(1170, UNITS.Milliliter))


if __name__ == '__main__':
  unittest.main()
