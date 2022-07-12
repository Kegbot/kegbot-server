import copy

from addict import Dict
from django.test import TransactionTestCase
from django.test.utils import override_settings

from pykeg.backend import get_kegbot_backend

from . import models
from .testutils import make_datetime


@override_settings(KEGBOT_BACKEND="pykeg.core.testutils.TestBackend")
class StatsTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.backend = get_kegbot_backend()
        models.User.objects.create_user("guest")

        test_usernames = ("user1", "user2", "user3")
        self.users = [
            self.backend.create_new_user(name, "%s@example.com" % name) for name in test_usernames
        ]

        self.taps = [
            self.backend.create_tap("tap1", "kegboard.flow0", ticks_per_ml=2.2),
            self.backend.create_tap("tap2", "kegboard.flow1", ticks_per_ml=2.2),
        ]

        self.keg = self.backend.start_keg(
            "kegboard.flow0",
            beverage_name="Unknown",
            beverage_type="beer",
            producer_name="Unknown",
            style_name="Unknown",
        )

    def testStuff(self):
        site = models.KegbotSite.get()
        stats = site.get_stats()
        self.assertEqual(stats, {})

        now = make_datetime(2012, 1, 2, 12, 00)
        self.maxDiff = None

        d = self.backend.record_drink(
            "kegboard.flow0", ticks=1, volume_ml=100, username="user1", pour_time=now
        )
        expected = Dict(
            {
                "volume_by_year": {"2012": 100.0},
                "total_pours": 1,
                "has_guest_pour": False,
                "greatest_volume_ml": 100.0,
                "registered_drinkers": ["user1"],
                "volume_by_day_of_week": {"1": 100.0},
                "greatest_volume_id": d.id,
                "volume_by_drinker": {"user1": 100.0},
                "volume_by_session": {"1": 100.0},
                "last_drink_id": d.id,
                "keg_ids": [d.keg.id],
                "sessions_count": 1,
                "average_volume_ml": 100.0,
                "total_volume_ml": 100.0,
                "largest_session": {"session_id": 1, "volume_ml": 100},
            }
        )
        stats = site.get_stats()
        self.assertDictEqual(expected, stats)

        now = make_datetime(2012, 1, 3, 12, 00)
        d = self.backend.record_drink(
            "kegboard.flow0", ticks=200, volume_ml=200, username="user2", pour_time=now
        )
        stats = site.get_stats()
        expected.total_pours = 2
        expected.greatest_volume_ml = 200.0
        expected.greatest_volume_id = d.id
        expected.registered_drinkers.append("user2")
        expected.volume_by_drinker["user2"] = 200.0
        expected.last_drink_id = d.id
        expected.average_volume_ml = 150.0
        expected.total_volume_ml = 300.0
        expected.volume_by_day_of_week["2"] = 200.0
        expected.volume_by_year["2012"] = 300.0
        expected.sessions_count = 2
        expected.volume_by_session = {"1": 100.0, "2": 200.0}
        expected.largest_session = {"session_id": 2, "volume_ml": 200.0}

        self.assertDictEqual(expected, stats)

        d = self.backend.record_drink(
            "kegboard.flow0", ticks=300, volume_ml=300, username="user2", pour_time=now
        )

        stats = site.get_stats()
        expected.total_pours = 3
        expected.greatest_volume_ml = 300.0
        expected.greatest_volume_id = d.id
        expected.volume_by_drinker["user2"] = 500.0
        expected.last_drink_id = d.id
        expected.average_volume_ml = 200.0
        expected.total_volume_ml = 600.0
        expected.volume_by_day_of_week["2"] = 500.0
        expected.volume_by_year["2012"] = 600.0
        expected.sessions_count = 2
        expected.volume_by_session = {"1": 100.0, "2": 500.0}
        expected.largest_session = {"session_id": 2, "volume_ml": 500.0}

        self.assertDictEqual(expected, stats)
        previous_stats = copy.copy(stats)

        d = self.backend.record_drink("kegboard.flow0", ticks=300, volume_ml=300, pour_time=now)

        stats = site.get_stats()
        self.assertTrue(stats.has_guest_pour)

        self.backend.cancel_drink(d)
        stats = site.get_stats()

        self.assertDictEqual(previous_stats, stats)

    def test_cancel_and_reassign(self):
        drink_data = [
            (100, self.users[0]),
            (200, self.users[1]),
            (200, self.users[2]),
            (500, self.users[0]),
        ]

        drinks = []

        now = make_datetime(2012, 1, 2, 12, 00)
        for volume_ml, user in drink_data:
            d = self.backend.record_drink(
                "kegboard.flow0",
                ticks=volume_ml,
                username=user.username,
                volume_ml=volume_ml,
                pour_time=now,
            )
            drinks.append(d)

        self.assertEqual(600, self.users[0].get_stats().total_volume_ml)
        self.assertEqual(200, self.users[1].get_stats().total_volume_ml)
        self.assertEqual(200, self.users[2].get_stats().total_volume_ml)

        self.assertEqual(1000, models.KegbotSite.get().get_stats().total_volume_ml)

        self.backend.cancel_drink(drinks[0])
        self.assertEqual(500, self.users[0].get_stats().total_volume_ml)
        self.assertEqual(200, self.users[1].get_stats().total_volume_ml)
        self.assertEqual(200, self.users[2].get_stats().total_volume_ml)
        self.assertEqual(900, models.KegbotSite.get().get_stats().total_volume_ml)

        self.backend.assign_drink(drinks[1], self.users[0])
        self.assertEqual(700, self.users[0].get_stats().total_volume_ml)
        self.assertEqual({}, self.users[1].get_stats())
        self.assertEqual(200, self.users[2].get_stats().total_volume_ml)
        self.assertEqual(900, models.KegbotSite.get().get_stats().total_volume_ml)
        self.assertEqual(900, drinks[1].session.get_stats().total_volume_ml)

        # Start a new session.
        now = make_datetime(2013, 1, 2, 12, 00)
        for volume_ml, user in drink_data:
            d = self.backend.record_drink(
                "kegboard.flow0",
                ticks=volume_ml,
                username=user.username,
                volume_ml=volume_ml,
                pour_time=now,
            )
            drinks.append(d)

        self.assertEqual(1300, self.users[0].get_stats().total_volume_ml)
        self.assertEqual(200, self.users[1].get_stats().total_volume_ml)
        self.assertEqual(400, self.users[2].get_stats().total_volume_ml)
        self.assertEqual(1900, models.KegbotSite.get().get_stats().total_volume_ml)
        self.assertEqual(1000, drinks[-1].session.get_stats().total_volume_ml)

        # Delete all stats for some intermediate drinks.
        models.Stats.objects.filter(drink=drinks[-1]).delete()
        models.Stats.objects.filter(drink=drinks[-2]).delete()

        d = self.backend.record_drink(
            "kegboard.flow0", ticks=1111, username=user.username, volume_ml=1111, pour_time=now
        )
        drinks.append(d)

        # Intermediate stats are generated.
        self.assertEqual(3011, models.KegbotSite.get().get_stats().total_volume_ml)
        self.assertEqual(2111, drinks[-1].session.get_stats().total_volume_ml)

    def test_timezone_awareness(self):
        site = models.KegbotSite.get()
        site.timezone = "US/Pacific"
        site.save()

        drink_data = [
            (100, self.users[0]),
            (200, self.users[1]),
            (200, self.users[2]),
            (500, self.users[0]),
        ]

        drinks = []

        # 1 AM UTC
        now = make_datetime(2012, 1, 2, 1, 0)
        for volume_ml, user in drink_data:
            d = self.backend.record_drink(
                "kegboard.flow0",
                ticks=volume_ml,
                username=user.username,
                volume_ml=volume_ml,
                pour_time=now,
            )
            drinks.append(d)
            self.assertEqual("US/Pacific", d.session.timezone)

        stats = site.get_stats()
        # Assert that stats are recorded for Sunday (day = 0) rather than
        # UTC's monday (day = 1).
        self.assertEqual({"0": 1000.0}, stats.volume_by_day_of_week)
        self.assertEqual(600, self.users[0].get_stats().total_volume_ml)
