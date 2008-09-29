#!/usr/bin/python2.4

"""
This script will regenerate the binges table.

Usage:
   $ recalc_binges.py mysql://root:password@localhost/kegbot
"""

import sys
import time

import Backend

def AssignToBinges(drinks):
   last_bid = None
   for drink in drinks:
      if drink.status != 'valid':
         continue
      bid = Backend.Binge.Assign(drink)
      if bid != last_bid:
         sys.stdout.write('\n+++ new binge %i: ' % bid)
      last_bid = bid
      sys.stdout.write('.')
      sys.stdout.flush()
   print ''

def Main():
   Backend.setup(sys.argv[1])
   Backend.drop_and_create(Backend.Binge)
   drinks = Backend.Drink.select(orderBy="endtime")
   AssignToBinges(drinks)

Main()
