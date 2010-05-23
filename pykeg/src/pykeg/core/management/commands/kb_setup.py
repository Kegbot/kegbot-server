from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.contrib.auth.management.commands import createsuperuser

from south.management.commands import migrate
from south.management.commands import syncdb
from pykeg.core.management.commands import kb_set_defaults


class Command(BaseCommand):
  help = u'Run basic Kegbot setup.'
  args = '<none>'

  def handle(self, *args, **options):
    if len(args) != 0:
      raise CommandError('No arguments required')

    # syncdb
    options = {'--all':'', '--noinput':''}
    print '--- Running syncdb %s' % ' '.join(options.keys())
    syncdb.Command().execute(**options)

    # migrate
    options = {'--all': '', '--fake': ''}
    print '--- Running migrate %s' % ' '.join(options.keys())
    migrate.Command().execute(**options)

    # kb_set_defaults
    options = {}
    print '--- Running kb_set_defaults'
    kb_set_defaults.Command().execute(**options)

