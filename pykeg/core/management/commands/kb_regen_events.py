# Copyright 2014 Bevbot LLC, All Rights Reserved
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

from pykeg.core import models
from pykeg.core.management.commands.common import progbar


class Command(BaseCommand):
    help = u'Regenerate all system events.'

    def handle(self, *args, **options):
        events = models.SystemEvent.objects.all()
        num_events = len(events)
        progbar('clear events', 0, num_events)
        events.delete()
        progbar('clear events', num_events, num_events)
        print ''

        pos = 0
        drinks = models.Drink.objects.all()
        count = drinks.count()
        for d in drinks.order_by('time'):
            pos += 1
            progbar('create new events', pos, count)
            models.SystemEvent.build_events_for_drink(d)
        print ''

        print 'done!'
