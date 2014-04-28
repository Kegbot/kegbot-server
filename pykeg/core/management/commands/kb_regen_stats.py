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
        stats.invalidate_all()

        drinks = models.Drink.objects.all().order_by('id')
        num_drinks = len(drinks)
        pos = 0
        for d in drinks:
            pos += 1
            progbar('regenerating stats', pos, num_drinks)
            stats.generate(d, invalidate_first=False)

        print ''
        print 'done!'
