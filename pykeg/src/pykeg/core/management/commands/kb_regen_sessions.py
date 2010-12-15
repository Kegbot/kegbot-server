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

from django.db import connection
from django.core.management.base import CommandError
from django.core.management.base import NoArgsCommand

from pykeg.core import models
from pykeg.core.management.commands.common import progbar

class Command(NoArgsCommand):
  help = u'Regenerate all cached stats.'
  args = '<none>'

  def handle(self, **options):
    drinks = models.Drink.objects.valid()

    pos = 0
    count = drinks.count()
    for d in drinks:
      pos += 1
      progbar('clear drink sessions', pos, count)
      d.session = None
      d.save()
    print ''

    print 'deleting old sessions..',
    try:
      cursor = connection.cursor()
      for table in ('core_drinkingsession', 'core_kegsessionchunk',
        'core_usersessionchunk', 'core_sessionchunk'):
        cursor.execute('TRUNCATE TABLE `%s`' % table)
      print 'truncate successful'
    except Exception, e:
      models.DrinkingSession.objects.all().delete()
      print 'orm delete successful'

    pos = 0
    count = drinks.count()
    for d in drinks.order_by('starttime'):
      pos += 1
      progbar('calc new sessions', pos, count)
      sess = models.DrinkingSession.AssignSessionForDrink(d)
    print ''

    print 'done!'
