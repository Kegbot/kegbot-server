# Copyright 2011 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

import datetime

from pykeg.core import models


class Command(BaseCommand):
  help = u'Deletes any old temperature sensor records'
  args = '<none>'

  def handle(self, *args, **options):
    if len(args) != 0:
      raise CommandError('No arguments required')

    now = datetime.datetime.now()

    # keep at least the most recent 24 hours
    keep_time = now - datetime.timedelta(hours=24)

    # round down to the start of the day
    keep_date = datetime.datetime(year=keep_time.year, month=keep_time.month,
        day=keep_time.day)

    print "Deleting entries older than %s" % keep_date

    for sensor in models.ThermoSensor.objects.all():
      old_entries = sensor.thermolog_set.filter(time__lt=keep_date).order_by('time')
      print "Sensor: %s" % sensor
      print "Deleting %s entries ..." % (old_entries.count())
      old_entries.delete()
      print ""
