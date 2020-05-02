from __future__ import print_function

from builtins import input
from django.conf import settings
from django.core.management.base import BaseCommand
from pykeg.backup import backup

import sys


class Command(BaseCommand):
    help = "Erases all data in the current Kegbot system."

    def handle(self, *args, **options):
        print("WARNING!")
        print("")
        print("  ************************************************************************")
        print("  This command erases ALL tables and media files in the Kegbot system, and ")
        print("  CANNOT BE UNDONE.")
        print("")
        print("    Database: {}".format(settings.DATABASES["default"]["NAME"]))
        print("       Media: {}".format(settings.MEDIA_ROOT))
        print("  ************************************************************************")
        print("")
        print("Are you SURE you want to continue? ")
        print("")

        try:
            response = input("Type ERASE to continue, anything else to abort: ")
        except KeyboardInterrupt:
            response = ""
        print("")
        if response.strip() != "ERASE":
            print("Aborted.")
            sys.exit(1)
        backup.erase()
