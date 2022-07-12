import os

from django.core.files.storage import get_storage_class
from django.core.management.base import BaseCommand

from pykeg.backend.backends import UnknownBaseUrlException
from pykeg.backup import backup


class Command(BaseCommand):
    help = "Creates a zipfile backup of the current Kegbot system."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no_media",
            action="store_true",
            dest="no_media",
            default=False,
            help="Skip media during backup.",
        )

    def handle(self, **options):
        location = backup.backup(include_media=not options.get("no_media"))
        storage = get_storage_class()()

        path = location
        if hasattr(storage, "location"):
            path = os.path.join(storage.location, path)
        print("Backup complete!")
        print("Path: {}".format(path))
        try:
            print("URL: {}".format(storage.url(location)))
        except (NotImplementedError, UnknownBaseUrlException):
            pass
