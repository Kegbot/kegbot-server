#!/usr/bin/env python

"""Set date joined of each User to first drink date"""

from pykeg.core import models

for user in models.User.objects.all():
  q = models.Drink.objects.filter(user=user).order_by('starttime')
  if len(q):
    first_drink = q[0]
    if first_drink.starttime < user.date_joined:
      print '%s: joined %s' % (user.username, first_drink.starttime)
      user.date_joined = first_drink.starttime
      user.save()

