from __future__ import print_function

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from pykeg.core import models


class Command(BaseCommand):
    args = "<from> <to>"
    help = "Renames user from <from> to <to>."

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError("Must specify <from> and <to>")

        from_username = args[0]
        to_username = args[1]

        if from_username == "guest":
            raise CommandError("Cannot rename the guest user.")

        with transaction.atomic():
            try:
                user = models.User.objects.get(username=from_username)
            except models.User.DoesNotExist:
                raise CommandError('User named "{}" does not exist'.format(from_username))

            user.username = to_username
            user.save()

        print('"{}" has been renamed "{}"'.format(from_username, to_username))
