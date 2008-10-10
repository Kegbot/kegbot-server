#!/usr/bin/env python

"""Set keg start and end times according to drinks."""

from pykeg.core import models

for keg in models.Keg.objects.all():
  q = models.Drink.objects.filter(keg=keg).order_by('starttime')
  dirty = False
  if not len(q):
    continue

  first_drink = q[0]
  last_drink = q[len(q)-1]
  if keg.startdate != first_drink.starttime:
    keg.startdate = first_drink.starttime
    dirty = True
  if keg.enddate != last_drink.endtime:
    keg.enddate = last_drink.endtime
    dirty = True
  if dirty:
    keg.save()
    print '%s: %s to %s' % (keg, keg.startdate, keg.enddate)

