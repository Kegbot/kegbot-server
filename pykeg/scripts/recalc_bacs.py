#!/usr/bin/python2.4

"""
This script will regenerate the binges table.

Usage:
   $ recalc_binges.py mysql://root:password@localhost/kegbot
"""

import sys
import time

import Backend

def Main():
   Backend.setup(sys.argv[1])
   Backend.drop_and_create(Backend.BAC)
   drinks = Backend.Drink.select('status="valid"', orderBy='starttime')
   for drink in drinks:
      Backend.BAC.ProcessDrink(drink)

Main()
