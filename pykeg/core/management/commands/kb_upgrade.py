# Copyright 2012 Mike Wakerly <opensource@hoho.com>
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

import sys

from pykeg import EPOCH

from django.core.management.base import NoArgsCommand
from django.db import connection

from django.contrib.staticfiles.management.commands import collectstatic
from south.management.commands import migrate
from south.management.commands import syncdb
from pykeg.core.management.commands import kb_regen_stats
from pykeg.core import models

def run(cmd, args=[]):
    cmdname = cmd.__module__.split('.')[-1]
    arg_str = ' '.join('%s' % a for a in args)
    print '--- Running command: %s %s' % (cmdname, arg_str)
    cmd.run_from_argv([sys.argv[0], cmdname] + args)

class Command(NoArgsCommand):
    help = u'Perform post-upgrade tasks.'

    def handle(self, **options):
        self.do_epoch_upgrades()
        run(syncdb.Command(), args=['--noinput', '-v', '0'])
        run(migrate.Command(), args=['-v', '0'])
        run(kb_regen_stats.Command())
        run(collectstatic.Command(), args=['--noinput'])

        site = models.KegbotSite.get()
        site.epoch = EPOCH
        site.save()

    def do_epoch_upgrades(self):
        installed = models.KegbotSite.get().epoch
        if installed == EPOCH or not installed:
            return

        print 'Performing epoch upgrades ...'
        for version in range(installed + 1, EPOCH + 1):
            fn = getattr(self, 'to_%s' % version, None)
            if fn:
                print '  ~ %s' % version
                fn()
            else:
                print '  ~ %s (no-op)' % version

    def to_101(self):
        cursor = connection.cursor()
        cursor.execute('DELETE FROM south_migrationhistory WHERE app_name = %s', ['twitter'])

    def to_102(self):
        cursor = connection.cursor()
        cursor.execute('DELETE FROM south_migrationhistory WHERE app_name = %s', ['foursquare'])

    def to_103(self):
        cursor = connection.cursor()
        cursor.execute('DELETE FROM south_migrationhistory WHERE app_name = %s', ['untappd'])
