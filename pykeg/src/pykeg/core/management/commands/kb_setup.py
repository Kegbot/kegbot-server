# Copyright 2011 Mike Wakerly <opensource@hoho.com>
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

from django.core.management.base import NoArgsCommand
from django.core.management.base import CommandError
from django.contrib.auth.management.commands import createsuperuser
from django.db.utils import DatabaseError

from south.management.commands import migrate
from south.management.commands import syncdb
from pykeg.core.management.commands import kb_set_defaults

from pykeg.core import backend
from pykeg.core import defaults


class Command(NoArgsCommand):
  help = u'Run basic Kegbot setup.'

  def handle(self, **options):
    installed = False
    try:
      b = backend.KegbotBackend()
      installed = defaults.db_is_installed()
    except backend.BackendError, e:
      pass
    except DatabaseError:
      pass

    if installed:
      print 'Error: Kegbot appears to be already installed. ',
      print 'Try "%s kb_upgrade" instead?' % (sys.argv[0],)
      sys.exit(1)

    self.InitialSetup()

  def _RunCommand(self, cmd, args=None):
    if args is None:
      args = []
    cmdname = cmd.__module__.split('.')[-1]
    arg_str = ' '.join('%s' % a for a in args)
    print '--- Running command: %s %s' % (cmdname, arg_str)
    cmd.run_from_argv([sys.argv[0], cmdname] + args)

  def InitialSetup(self):
    # syncdb
    self._RunCommand(syncdb.Command(), args=['--all', '--noinput', '-v', '0'])

    # migrate
    self._RunCommand(migrate.Command(), args=['--all', '--fake', '-v', '0'])

    # kb_set_defaults
    self._RunCommand(kb_set_defaults.Command(), args=['--force'])
