from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

import datetime

from pykeg.core import models


class Command(BaseCommand):
  help = u'Compress temperature records'
  args = '<none>'

  def handle(self, *args, **options):
    if len(args) != 0:
      raise CommandError('No arguments required')

    models.Thermolog.CompressLogs()
