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
from optparse import make_option

from pykeg.util.runner import Runner
import os
import sys

class Command(BaseCommand):
    help = u'Runs workers.'

    requires_model_validation = False

    option_list = BaseCommand.option_list + (
        make_option('--logs_dir', action='store', dest='logs_dir', default='',
            help='Specifies the directory for log files.  If empty, logging disabled.'),
        make_option('--pid_file', action='store', dest='pid_file', default='/tmp/kegbot_run_workers.pid',
            help='PID file for this program.'),
    )

    def handle(self, *args, **options):
        pid_file = options['pid_file']
        if os.path.exists(pid_file):
            print 'Error: run_workers already running ({})'.format(pid_file)
            sys.exit(1)

        f = open(pid_file, 'w')
        f.write('{}\n'.format(os.getpid()))
        f.close()

        try:
            default_log = stats_log = ''
            logs_dir = options.get('logs_dir')
            if logs_dir:
                default_log = ' --logfile="{}"'.format(
                    os.path.join(logs_dir, 'celery_default.log'))
                stats_log = ' --logfile="{}"'.format(
                    os.path.join(logs_dir, 'celery_stats.log'))

            r = Runner()
            r.add_command('celery_default',
                'celery -A pykeg worker -l info -Q default --hostname="default@%h"' + default_log)
            r.add_command('celery_stats',
                'celery -A pykeg worker -l info -Q stats --concurrency=1 --hostname="stats@%h"' +stats_log)
            r.run()
        finally:
            os.unlink(pid_file)
