from django.core.management.base import BaseCommand

from pykeg.core import models
from pykeg.core.management.commands.common import progbar


class Command(BaseCommand):
    help = "Regenerate all system events."

    def handle(self, *args, **options):
        events = models.SystemEvent.objects.all()
        num_events = len(events)
        progbar("clear events", 0, num_events)
        events.delete()
        progbar("clear events", num_events, num_events)
        print("")

        pos = 0
        drinks = models.Drink.objects.all()
        count = drinks.count()
        for d in drinks.order_by("time"):
            pos += 1
            progbar("create new events", pos, count)
            models.SystemEvent.build_events_for_drink(d)
        print("")

        print("done!")
