from __future__ import print_function

from django.core.management.base import BaseCommand
from django.db import transaction

from pykeg.core import models
from pykeg.core import stats
from pykeg.core.management.commands.common import progbar


class Command(BaseCommand):
    help = "Regenerate all cached stats."

    @transaction.atomic
    def handle(self, *args, **options):
        num_drinks = models.Drink.objects.all().count()
        self.pos = 0

        def cb(results, self=self):
            self.pos += 1
            progbar("regenerating stats", self.pos, num_drinks)

        stats.invalidate_all()
        stats.rebuild_from_id(0, cb=cb)

        print("")
        print("done!")
