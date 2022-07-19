import datetime
import itertools
import logging

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from freezegun import freeze_time

from pykeg.core import defaults, models

logger = logging.getLogger(__name__)

FAKE_TIME = "2022-03-04"
FIXTURE_PASSWORD = "!unusable-fixture-user-password"
FIXTURE_OUTPUT_FILENAME = "testdata/demo-site.json"


class Command(BaseCommand):
    f"""Generates the file {FIXTURE_OUTPUT_FILENAME} with fake data."""

    @freeze_time("2022-03-04")
    def handle(self, *args, **options):
        if settings.KEGBOT_ENV != "test":
            raise ValueError("Can only run this command in test mode!")
        call_command("migrate")
        self.create_objects()
        call_command(
            "dumpdata",
            "core",
            format="json",
            indent=2,
            output="testdata/demo-site.json",
        )

    def create_objects(self):
        defaults.set_defaults(set_is_setup=True, create_controller=True)
        user = models.User.objects.create(
            username="admin", email="admin@example.com", is_superuser=True, is_staff=True
        )
        guest_user = models.User.objects.get(username="guest")

        # If we call `.set_unusable_password()`, we'll get a new random (unusable)
        # password every time this script is run. The password for the fake user
        # isn't important either way in tests, so just crib an unusable password here.
        # (It's not documented, but Django should treat a prefix of "!" as unusable.)
        user.password = FIXTURE_PASSWORD
        user.save()
        guest_user.password = FIXTURE_PASSWORD
        guest_user.save()

        producer1 = models.BeverageProducer.objects.create(name="Test Producer 1")
        producer2 = models.BeverageProducer.objects.create(name="Test Producer 2")
        beverage1 = models.Beverage.objects.create(name="Test Beverage 1", producer=producer1)
        beverage2 = models.Beverage.objects.create(name="Test Beverage 2", producer=producer2)

        keg1 = models.Keg.start_keg("kegboard.flow0", beverage1)
        keg2 = models.Keg.start_keg("kegboard.flow1", beverage2)

        users = {"alice": None, "bob": None, "carol": None, "mallory": None}
        for username in users.keys():
            user = models.User.create_new_user(username=username, email=f"{username}@example.com")
            user.password = FIXTURE_PASSWORD
            user.activation_key = ""
            user.save()
            users[username] = user

        delay_generator = itertools.cycle([1, 2, 4, 3, 16, 1440])
        tick_generator = itertools.cycle([120, 200, 300, 500, 25, 500])
        meter_generator = itertools.cycle(["kegboard.flow0", "kegboard.flow0", "kegboard.flow1"])
        user_generator = itertools.cycle(users.values())
        with freeze_time(FAKE_TIME) as frozen_datetime:
            for _ in range(50):
                user = next(user_generator)
                delay = next(delay_generator)
                ticks = next(tick_generator)
                meter = next(meter_generator)
                models.Drink.record_drink(meter, ticks, username=user.username)
                frozen_datetime.tick(delta=datetime.timedelta(minutes=delay))
