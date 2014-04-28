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

from pykeg.core.management.commands.common import RunnerCommand
from optparse import make_option


class Command(RunnerCommand):
    help = u'Runs background task queue workers.'
    pidfile_name = 'kegbot_run_all.pid'

    option_list = RunnerCommand.option_list + (
        make_option('--gunicorn_options', action='store', dest='gunicorn_options', default='-w 3',
            help='Specifies extra options to pass to gunicorn.'),
    )

    def get_commands(self, options):
        ret = []
        logs_dir = options.get('logs_dir')

        workers_command = 'kegbot run_workers'
        if logs_dir:
            workers_command += ' --logs_dir={}'.format(logs_dir)
        ret.append(('workers', workers_command))

        extra_options = options.get('gunicorn_options', '')
        ret.append(('guincorn', 'kegbot run_gunicorn --settings=pykeg.settings ' + extra_options))
        return ret
