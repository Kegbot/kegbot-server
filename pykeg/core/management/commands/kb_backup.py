# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pykeg.core import backup
from pykeg.core import models

from optparse import make_option

class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
      make_option('-s', '--site',
        type='string',
        action='store',
        dest='site',
        default='default',
        help='Site to load to/from.'),
      make_option('-d', '--dump',
        type='string',
        action='store',
        dest='dump',
        help='Filename to dump to (dump mode).'),
      make_option('-r', '--restore',
        type='string',
        action='store',
        dest='restore',
        help='Filename to restore from (restore mode).'),
      make_option('-i', '--indent',
        action='store_true',
        dest='indent',
        default=True,
        help='Indent and pretty-print the output.'),
      )

  help = """Kegbot dump/restore tool. WARNING: Experimental."""
  args = '<none>'

  def handle(self, **options):
    if not options['site']:
      raise CommandError('Must give --site')

    if not (bool(options['dump']) ^ bool(options['restore'])):
      raise CommandError('Must give exactly one of: --dump=<filename>, --restore=<filename>')

    kbsite = self.prep_site(options['site'], options['restore'])

    if options['restore']:
      input_fp = open(options['restore'], 'r')
      backup.restore(input_fp, kbsite, self.debug)
      input_fp.close()
    else:
      indent = None
      if options['indent']:
        indent = 2
      output_fp = open(options['dump'], 'w')
      backup.dump(output_fp, kbsite, indent, self.debug)
      output_fp.close()

  def prep_site(self, sitename, restore):
    if restore:
      if models.KegbotSite.objects.filter(name=sitename).count():
        raise CommandError('Cannot restore: Site "%s" already exists; delete '
            'with kb_delete_site first ' % (sitename,))
      kbsite = models.KegbotSite.objects.create(name=sitename)
    else:
      try:
        kbsite = models.KegbotSite.objects.get(name=sitename)
      except models.KegbotSite.DoesNotExist:
        raise CommandError('Cannot dump: Site "%s" does not exist' % (sitename,))

  def debug(self, msg):
    print msg

