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

from optparse import make_option
import sys

from pykeg import EPOCH

from django.core.management.base import NoArgsCommand
from django.core.management.base import CommandError
from django.contrib.auth.management.commands import createsuperuser
from django.db.utils import DatabaseError

from django.contrib.staticfiles.management.commands import collectstatic
from south.management.commands import migrate
from south.management.commands import syncdb
from pykeg.core.management.commands import kb_regen_stats

def run(cmd, args=[]):
  cmdname = cmd.__module__.split('.')[-1]
  arg_str = ' '.join('%s' % a for a in args)
  print '--- Running command: %s %s' % (cmdname, arg_str)
  cmd.run_from_argv([sys.argv[0], cmdname] + args)

class Command(NoArgsCommand):
  help = u'Perform post-upgrade tasks.'

  def handle(self, **options):
    run(syncdb.Command(), args=['--noinput', '-v', '0'])
    run(migrate.Command(), args=['-v', '0'])
    run(kb_regen_stats.Command())
    run(collectstatic.Command())

    from pykeg.core import models
    for site in models.KegbotSite.objects.all():
      site.epoch = EPOCH
      site.save()
