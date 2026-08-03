from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from pykeg.core import models


class Command(BaseCommand):
    help = "Renames user from <from> to <to>."

    def add_arguments(self, parser):
        parser.add_argument("from_username", metavar="from")
        parser.add_argument("to_username", metavar="to")

    def handle(self, *args, **options):
        from_username = options["from_username"]
        to_username = options["to_username"]

        if from_username == "guest":
            raise CommandError("Cannot rename the guest user.")

        with transaction.atomic():
            try:
                user = models.User.objects.get(username=from_username)
            except models.User.DoesNotExist:
                raise CommandError(f'User named "{from_username}" does not exist')

            user.username = to_username
            user.save()

        print(f'"{from_username}" has been renamed "{to_username}"')
