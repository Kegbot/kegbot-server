import os
import sys

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from pykeg.backup import backup


class Command(BaseCommand):
    help = "Restores a zipfile backup of the current Kegbot system."
    args = "<zipfile>"

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Must provide a zipfile path")
        backup_path = os.path.normpath(os.path.expanduser(args[0]))
        if not os.path.exists(backup_path):
            raise CommandError("Archive does not exist: {}".format(backup_path))

        try:
            backup.restore(backup_path)
        except backup.AlreadyInstalledError:
            sys.stderr.write("Error: Kegbot is already installed, run `kegbot erase` first.")
            sys.stderr.write("\n")
            sys.exit(1)
        except backup.BackupError as e:
            sys.stderr.write("Error: ")
            sys.stderr.write(e)
            sys.stderr.write("\n")
            sys.exit(1)
