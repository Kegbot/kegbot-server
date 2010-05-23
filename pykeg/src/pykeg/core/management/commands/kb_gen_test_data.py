from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

import datetime

from pykeg.core import backend
from pykeg.core import defaults
from pykeg.core import models
from pykeg.core import units
from django.contrib.auth.models import User


class Command(BaseCommand):
  help = u'Generate test data in a new kegbot database.'
  args = '<none>'

  def handle(self, *args, **options):
    if len(args) != 0:
      raise CommandError('No arguments required')

    defaults.gentestdata()
