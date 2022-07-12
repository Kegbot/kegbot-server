from __future__ import print_function

from django.core.management.base import BaseCommand, CommandError

from pykeg.core import models


class Command(BaseCommand):
    args = "<description>"
    help = "Creates an API key with the given description."

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError("Must specify description")

        key = models.ApiKey.objects.create(description=args[0])
        print(key.key)
