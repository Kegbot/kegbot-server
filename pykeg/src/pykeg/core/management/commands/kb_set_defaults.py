from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pykeg.core import defaults

class Command(BaseCommand):
  help = u'Set defaults in a new kegbot database.'
  args = '<none>'

  def handle(self, *args, **options):
    if len(args) != 0:
      raise CommandError('No arguments required')

    if defaults.db_is_installed():
      print 'Error: database already installed, defaults cannot be set'
      return

    print 'Setting database defaults.'
    defaults.set_defaults()
