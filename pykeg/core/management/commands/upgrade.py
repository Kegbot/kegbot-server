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

from optparse import make_option
import sys

from pykeg import EPOCH
from pykeg.core.util import get_version

from django.core.management.base import BaseCommand
from django.db import connection

from django.contrib.staticfiles.management.commands import collectstatic
from south.management.commands import migrate
from south.management.commands import syncdb
from pykeg.core.management.commands import kb_regen_stats

from pykeg.core import models
from pykeg.core import checkin


def run(cmd, args=[]):
    cmdname = cmd.__module__.split('.')[-1]
    arg_str = ' '.join('%s' % a for a in args)
    print '--- Running command: %s %s' % (cmdname, arg_str)
    cmd.run_from_argv([sys.argv[0], cmdname] + args)


class Command(BaseCommand):
    help = u'Perform post-upgrade tasks.'
    option_list = BaseCommand.option_list + (
        make_option('--skip_static', action='store_true', dest='skip_static', default=False,
            help='Skip `kegbot collectstatic` during upgrade. (Not recommended.)'),
        make_option('--skip_stats', action='store_true', dest='skip_stats', default=False,
            help='Skip `kegbot kb_regen_stats` during upgrade. (Not recommended.)'),
    )

    def handle(self, *args, **options):
        self.do_epoch_upgrades()
        run(syncdb.Command(), args=['--noinput', '-v', '0'])
        run(migrate.Command(), args=['-v', '0'])

        if not options.get('skip_stats'):
            run(kb_regen_stats.Command())

        if not options.get('skip_static'):
            run(collectstatic.Command(), args=['--noinput'])

        site = models.KegbotSite.get()
        site.epoch = EPOCH
        site.server_version = get_version()
        site.save()

        # Refresh any news (since we have a new version).
        try:
            checkin.checkin(timeout=5.0, quiet=True)
        except (checkin.CheckinError, Exception):
            pass

        print ''
        print 'Upgrade complete!'

    def get_epoch(self):
        cursor = connection.cursor()
        cursor.execute("SELECT epoch FROM core_kegbotsite")
        row = cursor.fetchone()
        if not row:
            return None
        return int(row[0])

    def do_epoch_upgrades(self):
        installed = self.get_epoch()
        print '--- Current epoch: %s' % installed
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

    def to_104(self):
        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS djkombu_message')
        cursor.execute('DROP TABLE IF EXISTS djkombu_queue')
