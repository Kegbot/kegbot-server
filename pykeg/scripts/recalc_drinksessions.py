#!/usr/bin/env python

""" This script will regenerate the binges table. """

from pykeg.core import models

models.UserDrinkingSession.objects.all().delete()
models.UserDrinkingSessionAssignment.objects.all().delete()
models.DrinkingSessionGroup.objects.all().delete()

for d in models.Drink.objects.all().order_by('id'):
  assignment = models.UserDrinkingSessionAssignment.RecordDrink(d)
