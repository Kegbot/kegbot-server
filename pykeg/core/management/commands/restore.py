# Copyright 2014 Kegbot Project contributors
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
