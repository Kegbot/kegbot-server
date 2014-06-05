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

from django.core.management.base import NoArgsCommand
from django.db import transaction

from pykeg.core import models
from pykeg.core import stats
from pykeg.core.management.commands.common import progbar


class Command(NoArgsCommand):
    help = u'Regenerate all cached stats.'
    args = '<none>'

    @transaction.atomic
    def handle(self, **options):

        num_drinks = models.Drink.objects.all().count()
        self.pos = 0

        def cb(results, self=self):
            self.pos += 1
            progbar('regenerating stats', self.pos, num_drinks)

        stats.invalidate_all()
        stats.rebuild_from_id(0, cb=cb)

        print ''
        print 'done!'
