from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

import datetime

from pykeg.core import models


class Command(BaseCommand):
  help = u'Regenerate all cached stats.'
  args = '<none>'

  def print_stats(self, obj):
    print '--- %s' % obj
    for k in sorted(obj.stats.iterkeys()):
      v = obj.stats[k]
      print '  %-24s: %s' % (k, v)
    print ''

  def handle(self, *args, **options):
    if len(args) != 0:
      raise CommandError('No arguments required')

    models.UserStats.objects.all().delete()
    for user in models.User.objects.all():
      last_drinks = user.drink_set.all().order_by('-starttime')
      if last_drinks:
        user_stats = models.UserStats(user=user)
        user_stats.UpdateStats(last_drinks[0])
        user_stats.save()
        self.print_stats(user_stats)

    models.KegStats.objects.all().delete()
    for keg in models.Keg.objects.all():
      last_drinks = keg.drink_set.all().order_by('-starttime')
      if last_drinks:
        keg_stats = models.KegStats(keg=keg)
        keg_stats.UpdateStats(last_drinks[0])
        keg_stats.save()
        self.print_stats(keg_stats)
