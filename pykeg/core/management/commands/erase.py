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
from pykeg.core import backup

import sys


class Command(NoArgsCommand):
    help = u'Erases all data in the current Kegbot system.'

    def handle(self, **options):
        print 'This command erases ALL tables ad media files in the Kegbot system, and '
        print 'CANNOT BE UNDONE.'
        print ''
        print 'Are you SURE you want to continue? '
        print ''
        try:
            response = raw_input('Type ERASE to continue, anything else to abort: ')
        except KeyboardInterrupt:
            response = ''
        print ''
        if response.strip() != 'ERASE':
            print 'Aborted.'
            sys.exit(1)
        backup.erase()
