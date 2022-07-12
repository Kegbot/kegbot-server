from __future__ import division

import types
from builtins import object
from enum import Enum

from past.utils import old_div


class UNITS(Enum):
    Liter = 1000
    Milliliter = 1
    Microliter = 0.001
    Ounce = 29.57353
    Pint = 473.17648
    USGallon = 3785.411784
    ImperialGallon = 4546.09
    TwelveOunceBeer = 354.882
    HalfBarrelKeg = 58673.88
    KbMeterTick = 2.2  # aka Vision2000 (2200 pulses/liter)
    PonyKeg = 29336.94
    Cup = 236.588
    Quart = 946.353
    Hogshead = 238480.9434


class Quantity(object):
    def __init__(self, amount, units=UNITS.Milliliter, from_units=None):
        self._units = units
        self._amount = self.convert(amount, units, from_units) if from_units else amount
        for unit in UNITS:

            def fn(unit=unit):
                return self.ConvertTo(unit)._amount

            setattr(self, "In{}s".format(unit.name), fn)

    def __str__(self):
        return "{} {}".format(self._amount, self._units.name)

    def __add__(self, other, subtract=False):
        val = 0
        if isinstance(other, (int, float)):
            val += other
        elif isinstance(other, Quantity):
            val += other.ConvertTo(self._units)._amount
        else:
            raise TypeError
        if subtract:
            amount = self._amount - val
        else:
            amount = self._amount + val
        return Quantity(amount, self._units)

    def __sub__(self, other):
        return self.__add__(other, subtract=True)

    def __eq__(self, other):
        if isinstance(other, Quantity):
            if self._units == other._units:
                if self._amount == other._amount:
                    return True
        return False

    def __ne__(self, other):
        if isinstance(other, Quantity):
            if self._units == other._units and self._amount == other._amount:
                return False
        return True

    def __lt__(self, other):
        return self._amount < other.ConvertTo(self._units).Amount()

    def __le__(self, other):
        return self._amount <= other.ConvertTo(self._units).Amount()

    def __gt__(self, other):
        return self._amount > other.ConvertTo(self._units).Amount()

    def __ge__(self, other):
        return self._amount >= other.ConvertTo(self._units).Amount()

    # TODO: should have just subclassed float
    def __int__(self):
        return int(self.Amount())

    def __long__(self):
        return int(self.Amount())

    def __float__(self):
        return float(self.Amount())

    def units(self):
        return self._units

    def ConvertTo(self, to_units):
        if not to_units:
            raise ValueError("Bad to_units")
        amount = self.convert(self._amount, self._units, to_units)
        return Quantity(amount, to_units)

    def Amount(self):
        return self._amount

    @classmethod
    def convert(cls, amount, units_from, units_to):
        if not units_to:
            raise ValueError("Bad units_to")
        amount_in_ml = float(amount) * units_from.value
        return old_div(amount_in_ml, units_to.value)
