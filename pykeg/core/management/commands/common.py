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
import signal
import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from pykeg.util.runner import Runner


def progbar(title, pos, total, width=40):
    """Prints a progress bar to stdout.

    Args
      title: title to show next to progress bar
      pos: current position (integer)
      total: total positions (integer)
      width: width of the progres bar, in characters
    """
    if not sys.stdout.isatty():
        return
    if not total:
        chars = width
    else:
        chars = int((float(pos) / total) * width)
    rem = width - chars
    inner = '+' * chars + ' ' * rem
    sys.stdout.write('%-30s  [%s] %i/%i\r' % (title, inner, pos, total))
    sys.stdout.flush()


def check_and_create_pid_file(pid_file):
    if os.path.exists(pid_file):
        print 'Error: already running ({})'.format(pid_file)
        sys.exit(1)

    f = open(pid_file, 'w')
    f.write('{}\n'.format(os.getpid()))
    f.close()


class check_pidfile(object):
    """Context manager that creates a pidfile, or fails if it exists."""

    def __init__(self, pid_file):
        self.pid_file = pid_file

    def __enter__(self):
        if os.path.exists(self.pid_file):
            raise RuntimeError('Error: already running ({})'.format(self.pid_file))
        f = open(self.pid_file, 'w')
        f.write('{}\n'.format(os.getpid()))
        f.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.unlink(self.pid_file)


class RunnerCommand(BaseCommand):
    """Command that runs several subcommands as a watched group."""
    requires_model_validation = False

    option_list = BaseCommand.option_list + (
        make_option('--logs_dir', action='store', dest='logs_dir', default='',
            help='Specifies the directory for log files.  If empty, logging disabled.'),
        make_option('--pidfile_dir', action='store', dest='pidfile_dir', default='/tmp',
            help='PID file for this program.'),
    )

    pidfile_name = None

    def get_commands(self, options):
        """Returns iterable of (command_name, command)."""
        raise NotImplementedError

    def handle(self, *args, **options):
        pidfile = os.path.join(options['pidfile_dir'], self.pidfile_name)
        with check_pidfile(pidfile):
            r = Runner()

            def exit_fn(signum, frame):
                r.abort()
                sys.exit(1)

            signal.signal(signal.SIGTERM, exit_fn)
            signal.signal(signal.SIGINT, exit_fn)

            for command_name, command in self.get_commands(options):
                r.add_command(command_name, command)

            r.run()
