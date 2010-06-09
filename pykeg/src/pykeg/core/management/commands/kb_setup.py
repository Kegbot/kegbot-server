import sys

from django.core.management.base import NoArgsCommand
from django.core.management.base import CommandError
from django.contrib.auth.management.commands import createsuperuser

from south.management.commands import migrate
from south.management.commands import syncdb
from pykeg.core.management.commands import kb_set_defaults

from pykeg.core import backend


class Command(NoArgsCommand):
  help = u'Run basic Kegbot setup.'

  def handle(self, **options):
    cfg = None
    try:
      b = backend.KegbotBackend()
      cfg = b.GetConfig()
    except backend.BackendError, e:
      pass

    if cfg:
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
    self._RunCommand(kb_set_defaults.Command())
