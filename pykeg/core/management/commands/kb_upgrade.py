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

import time

from django.core.management.base import NoArgsCommand
from pykeg.core.management.commands import upgrade

class Command(NoArgsCommand):
    help = u'Deprecated; use "upgrade" instead.'

    def handle(self, **options):
        print 'Notice: "kb_upgrade" has been renamed "upgrade".\a'
        time.sleep(2)
        return upgrade.Command().handle(**options)

