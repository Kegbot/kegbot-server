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

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pykeg.core import defaults

class Command(BaseCommand):
  help = u'Set defaults in a new kegbot database.'
  args = '<none>'
  option_list = BaseCommand.option_list + (
      make_option('-f', '--force',
        action='store_true',
        dest='force',
        default=False,
        help='Forcibly set defaults (no database check).'),)

  def handle(self, *args, **options):
    if len(args) != 0:
      raise CommandError('No arguments required')

    try:
      defaults.set_defaults(options['force'])
    except RuntimeError:
      print 'Error: database already installed, defaults cannot be set'
      return
