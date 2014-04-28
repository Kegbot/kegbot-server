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

import os
from django.conf import settings

from pykeg.core.management.commands.common import RunnerCommand


class Command(RunnerCommand):
    help = u'Runs background task queue workers.'
    pidfile_name = 'kegbot_run_workers.pid'

    def get_commands(self, options):
        default_log = stats_log = beat_log = ''
        logs_dir = options.get('logs_dir')

        if logs_dir:
            default_log = ' --logfile="{}"'.format(
                os.path.join(logs_dir, 'celery_default.log'))
            stats_log = ' --logfile="{}"'.format(
                os.path.join(logs_dir, 'celery_stats.log'))
            beat_log = ' --logfile="{}"'.format(
                os.path.join(logs_dir, 'celery_beat.log'))
        ret = []

        # Pluck out the app_name.  Typically this is 'pykeg', but may be
        # something else in embedded mode.
        app_name = settings.SETTINGS_MODULE.split('.')[0]
        base_cmd = 'celery -A {} worker -l info '.format(app_name)

        ret.append(('celery_default',
            base_cmd + '-Q default --hostname="default@%h"' + default_log))
        ret.append(('celery_stats',
            base_cmd + '-Q stats --concurrency=1 --hostname="stats@%h"' + stats_log))

        ret.append(('celery_beat',
            'celery -A {} beat --pidfile= -l info{}'.format(app_name, beat_log)))

        return ret
