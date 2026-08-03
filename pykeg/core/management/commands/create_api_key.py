from django.core.management.base import BaseCommand

from pykeg.core import models


class Command(BaseCommand):
    help = "Creates an API key with the given description."

    def add_arguments(self, parser):
        parser.add_argument("description")

    def handle(self, *args, **options):
        key = models.ApiKey.objects.create(description=options["description"])
        print(key.key)
