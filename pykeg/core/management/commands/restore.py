import os
import sys

from django.core.management.base import BaseCommand, CommandError

from pykeg.backup import backup


class Command(BaseCommand):
    help = "Restores a zipfile backup of the current Kegbot system."

    def add_arguments(self, parser):
        parser.add_argument("zipfile")

    def handle(self, *args, **options):
        backup_path = os.path.normpath(os.path.expanduser(options["zipfile"]))
        if not os.path.exists(backup_path):
            raise CommandError(f"Archive does not exist: {backup_path}")

        try:
            backup.restore(backup_path)
        except backup.AlreadyInstalledError:
            sys.stderr.write("Error: Kegbot is already installed, run `kegbot erase` first.")
            sys.stderr.write("\n")
            sys.exit(1)
        except backup.BackupError as e:
            sys.stderr.write("Error: ")
            sys.stderr.write(str(e))
            sys.stderr.write("\n")
            sys.exit(1)
