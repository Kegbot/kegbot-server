#!/usr/bin/env python

""" This script will regenerate the binges table. """

from pykeg.core import models

for d in models.Drink.objects.all().order_by('id'):
  models.Binge.Assign(d)
