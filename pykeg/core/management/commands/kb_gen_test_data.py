# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

from django.core.management.base import NoArgsCommand

from pykeg.core import backend
from pykeg.core import models
from pykeg.core.management.commands.common import progbar

DRINKERS = (
  'mike', 'brian', 'dom', 'eric', 'ted', 'justin', None
)
NUM_DRINKS = 100
TAP = 'kegboard.flow0'

import time
import random
import datetime
from django.utils import timezone
BASE_TIME = timezone.now() - datetime.timedelta(days=365)

#import logging
#l = logging.getLogger('django.db.backends')
#l.setLevel(logging.DEBUG)
#l.addHandler(logging.StreamHandler())

class Command(NoArgsCommand):
    help = u'Generate fake data'
    args = '<none>'

    def handle(self, **options):
        profile = False
        if profile:
            import cProfile
            command = 'self.generate()'
            cProfile.runctx(command, globals(), locals())
        else:
            self.generate()

    def generate(self):
        num_drinks = 0
        num_sessions = 0

        now = BASE_TIME
        b = backend.KegbotBackend()
        while num_drinks < NUM_DRINKS:
            num_drinks += 1
            ticks = 400 + random.randrange(0, 400)
            username = random.choice(DRINKERS)
            if username:
                models.User.objects.get_or_create(username=username)

            start_time = time.time()
            d = b.RecordDrink(TAP, ticks, pour_time=now, username=username)
            delta = time.time() - start_time
            end_session = random.random() >= 0.75

            ms = int(delta * 1000)
            print '%s: %s: %s [%s]' % (ms, d.id, d.user, d.keg)

            if end_session:
                now += datetime.timedelta(hours=24 + random.randrange(0, 12))
            else:
                now += datetime.timedelta(minutes=random.randrange(3, 60))

            if d.keg.remaining_volume < 10000:
                b.EndKeg(TAP)
                b.StartKeg(TAP)
