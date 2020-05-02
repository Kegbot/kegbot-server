"""Unittests for backends module."""

from builtins import range
from django.test import TransactionTestCase
from pykeg.backend import get_kegbot_backend
from pykeg.core import models
from pykeg.core import defaults
from django.test.utils import override_settings

METER_NAME = "kegboard.flow0"
FAKE_BEER_NAME = "Testy Beer"
FAKE_BREWER_NAME = "Unittest Brewery"
FAKE_BEER_STYLE = "Test-Driven Pale Ale"

# Helper methods


@override_settings(KEGBOT_BACKEND="pykeg.core.testutils.TestBackend")
class BackendsFixtureTestCase(TransactionTestCase):
    """Test backened using fixture (demo) data."""

    fixtures = ["testdata/full_demo_site.json"]

    def setUp(self):
        self.backend = get_kegbot_backend()

    def test_delete_keg(self):
        site = models.KegbotSite.get()
        original_stats = site.get_stats()
        self.assertEqual(755, original_stats["total_pours"])

        keg = models.Keg.objects.get(pk=2)
        keg_stats = keg.get_stats()
        keg_drinks = keg.drinks.all()
        self.assertEqual(185, len(keg_drinks))
        self.backend.cancel_keg(keg)

        stats = site.get_stats()
        self.assertEqual(755 - 185, stats["total_pours"])
        self.assertEqual(
            original_stats["total_volume_ml"] - keg_stats["total_volume_ml"],
            stats["total_volume_ml"],
        )


@override_settings(KEGBOT_BACKEND="pykeg.core.testutils.TestBackend")
class BackendsTestCase(TransactionTestCase):
    """Test backend without canned data (legacy tests)."""

    def setUp(self):
        self.backend = get_kegbot_backend()
        defaults.set_defaults(set_is_setup=True, create_controller=True)

    def test_drink_management(self):
        """Test adding drinks."""
        tap = models.KegTap.get_from_meter_name(METER_NAME)
        tap.save()
        meter = tap.meter
        meter.ticks_per_ml = 2.2
        meter.save()
        keg = self.backend.start_keg(
            METER_NAME,
            beverage_name=FAKE_BEER_NAME,
            beverage_type="beer",
            producer_name=FAKE_BREWER_NAME,
            style_name=FAKE_BEER_STYLE,
        )
        self.assertIsNotNone(keg)

        self.assertEqual(0, keg.served_volume())
        drink = self.backend.record_drink(METER_NAME, ticks=2200)
        self.assertIsNotNone(drink)
        self.assertEqual(2200, drink.ticks)
        self.assertAlmostEqual(1000.0, drink.volume_ml, places=3)
        keg = models.Keg.objects.get(pk=keg.id)
        self.assertAlmostEqual(1000.0, keg.served_volume(), places=3)
        self.assertEqual("", drink.shout)
        self.assertEqual(0, drink.duration)

        drink = self.backend.record_drink(METER_NAME, ticks=1100)
        keg = models.Keg.objects.get(pk=keg.id)
        self.assertIsNotNone(drink)
        self.assertEqual(1100, drink.ticks)
        self.assertAlmostEqual(500.0, drink.volume_ml, places=3)
        self.assertAlmostEqual(1500.0, keg.served_volume(), places=3)

        # Add with volume, taking precedence over ticks.
        drink = self.backend.record_drink(METER_NAME, ticks=1100, volume_ml=1)
        keg = models.Keg.objects.get(pk=keg.id)
        self.assertIsNotNone(drink)
        self.assertEqual(1100, drink.ticks)
        self.assertAlmostEqual(1.0, drink.volume_ml, places=3)
        self.assertAlmostEqual(1501.0, keg.served_volume(), places=3)

        # Add with a user.
        user = models.User.objects.create(username="testy")
        drink = self.backend.record_drink(METER_NAME, ticks=2200, username=user.username)
        self.assertIsNotNone(drink)
        self.assertEqual(user, drink.user)

    def test_drink_cancel(self):
        """Tests cancelling drinks."""
        keg = self.backend.start_keg(
            METER_NAME,
            beverage_name=FAKE_BEER_NAME,
            beverage_type="beer",
            producer_name=FAKE_BREWER_NAME,
            style_name=FAKE_BEER_STYLE,
        )
        self.assertIsNotNone(keg)
        self.assertEqual(0, keg.served_volume())

        for i in range(10):
            self.backend.record_drink(METER_NAME, ticks=1, volume_ml=100)

        drinks = list(models.Drink.objects.all().order_by("id"))
        keg = models.Keg.objects.get(pk=keg.id)
        self.assertEqual(10, len(drinks))
        self.assertAlmostEqual(1000.0, keg.served_volume(), places=3)

        cancel_drink = drinks[-1]
        session = cancel_drink.session
        self.assertAlmostEqual(session.get_stats().total_volume_ml, 1000.0, places=3)

        self.backend.cancel_drink(drinks[-1])
        drinks = list(models.Drink.objects.all().order_by("id"))
        keg = models.Keg.objects.get(pk=keg.id)
        self.assertEqual(9, len(drinks))
        self.assertAlmostEqual(900.0, keg.served_volume(), places=3)
        session = models.DrinkingSession.objects.get(id=session.id)
        self.assertAlmostEqual(session.get_stats().total_volume_ml, 900.0, places=3)

        keg = models.Keg.objects.get(pk=keg.id)
        self.assertEqual(0, keg.spilled_ml)

        self.backend.cancel_drink(drinks[-1], spilled=True)
        keg = models.Keg.objects.get(pk=keg.id)
        drinks = list(models.Drink.objects.all().order_by("id"))
        self.assertEqual(8, len(drinks))
        self.assertAlmostEqual(800.0, keg.served_volume(), places=3)
        self.assertAlmostEqual(100.0, keg.spilled_ml, places=3)

        # Cancel all drinks and confirm the session is deleted.
        num_sessions = models.DrinkingSession.objects.all().count()
        first_drink, other_drinks = drinks[0], drinks[1:]
        for d in other_drinks:
            self.backend.cancel_drink(d)

        self.assertEqual(first_drink.volume_ml, first_drink.session.volume_ml)
        session_id = first_drink.session.id

        self.backend.cancel_drink(first_drink)

        with self.assertRaises(models.DrinkingSession.DoesNotExist):
            models.DrinkingSession.objects.get(pk=session_id)

        self.assertEqual(num_sessions - 1, models.DrinkingSession.objects.all().count())

    def test_reassign_drink_with_photo(self):
        keg = self.backend.start_keg(
            METER_NAME,
            beverage_name=FAKE_BEER_NAME,
            beverage_type="beer",
            producer_name=FAKE_BREWER_NAME,
            style_name=FAKE_BEER_STYLE,
        )
        self.assertIsNotNone(keg)
        self.assertEqual(0, keg.served_volume())

        drink = self.backend.record_drink(METER_NAME, ticks=1, volume_ml=100, photo="foo")

        self.assertTrue(drink.is_guest_pour())
        self.assertTrue(drink.user.is_guest())
        self.assertIsNotNone(drink.picture)
        self.assertTrue(drink.picture.user.is_guest())

        user = self.backend.create_new_user("blort", email="blort@example.com")
        updated_drink = self.backend.assign_drink(drink, user)
        self.assertEqual(user, updated_drink.user)
        self.assertEqual(user, updated_drink.picture.user)

    def test_keg_management(self):
        """Tests adding and removing kegs."""
        tap = models.KegTap.get_from_meter_name(METER_NAME)
        self.assertFalse(tap.is_active(), "Tap is already active.")

        # No beer types yet.
        qs = models.Beverage.objects.filter(name=FAKE_BEER_NAME)
        self.assertEqual(len(qs), 0, "Beverage already exists")

        # Tap the keg.
        keg = self.backend.start_keg(
            METER_NAME,
            beverage_name=FAKE_BEER_NAME,
            beverage_type="beer",
            producer_name=FAKE_BREWER_NAME,
            style_name=FAKE_BEER_STYLE,
        )
        self.assertIsNotNone(keg)
        self.assertTrue(keg.is_on_tap())

        self.assertEqual(keg.current_tap, tap, "Tap did not become active.")
        tap = keg.current_tap
        self.assertTrue(keg.current_tap.is_active())

        # Check that the beer type was created.
        qs = models.Beverage.objects.filter(name=FAKE_BEER_NAME)
        self.assertEqual(len(qs), 1, "Expected a single new Beverage.")
        beverage = qs[0]
        brewer = beverage.producer
        style = beverage.style
        self.assertEqual(brewer.name, FAKE_BREWER_NAME)
        self.assertEqual(style, FAKE_BEER_STYLE)

        # Now activate a new keg.
        keg = self.backend.end_keg(tap.current_keg)
        tap = models.KegTap.get_from_meter_name(METER_NAME)
        self.assertFalse(tap.is_active())
        self.assertFalse(keg.is_on_tap())

        new_keg = self.backend.start_keg(METER_NAME, beverage=beverage)
        tap = models.KegTap.get_from_meter_name(METER_NAME)
        self.assertIsNotNone(new_keg)
        self.assertNotEquals(new_keg, keg)
        self.assertTrue(tap.is_active())
        self.assertTrue(new_keg.is_on_tap())

        # Ensure the beer type was reused.
        self.assertEqual(new_keg.type, beverage)

        # Deactivate, and activate a new keg again by name.
        self.backend.end_keg(tap.current_keg)
        new_keg_2 = self.backend.start_keg(
            METER_NAME,
            beverage_name="Other Beer",
            beverage_type="beer",
            producer_name=FAKE_BREWER_NAME,
            style_name=FAKE_BEER_STYLE,
        )
        self.assertEqual(new_keg_2.type.producer, keg.type.producer)
        self.assertEqual(new_keg_2.type.style, keg.type.style)
        self.assertNotEquals(new_keg_2.type, keg.type)

        # New brewer, identical beer name == new beer type.
        tap = models.KegTap.get_from_meter_name(METER_NAME)
        self.backend.end_keg(tap.current_keg)
        new_keg_3 = self.backend.start_keg(
            METER_NAME,
            beverage_name=FAKE_BEER_NAME,
            beverage_type="beer",
            producer_name="Other Brewer",
            style_name=FAKE_BEER_STYLE,
        )
        self.assertNotEquals(new_keg_3.type.producer, keg.type.producer)
        self.assertEqual(new_keg_3.type.name, keg.type.name)
        self.assertNotEquals(new_keg_3.type, keg.type)

    def test_meters(self):
        tap = models.KegTap.objects.all()[0]
        meter = tap.current_meter()

        self.assertIsNotNone(meter)
        tap = self.backend.connect_meter(tap, None)
        self.assertIsNone(tap.current_meter())

        tap = self.backend.connect_meter(tap, meter)
        self.assertIsNotNone(tap.current_meter())

    def test_toggles(self):
        tap = models.KegTap.objects.all()[0]
        toggle = tap.current_toggle()

        self.assertIsNotNone(toggle)
        tap = self.backend.connect_toggle(tap, None)
        self.assertIsNone(tap.current_toggle())

        tap = self.backend.connect_toggle(tap, toggle)
        self.assertIsNotNone(tap.current_toggle())

    @override_settings(KEGBOT_BASE_URL="http://example.com:8000//")
    def test_urls(self):
        self.assertEqual("http://example.com:8000", self.backend.get_base_url())

        keg = self.backend.start_keg(
            METER_NAME,
            beverage_name=FAKE_BEER_NAME,
            beverage_type="beer",
            producer_name=FAKE_BREWER_NAME,
            style_name=FAKE_BEER_STYLE,
        )
        self.assertEqual("http://example.com:8000/kegs/{}".format(keg.id), keg.full_url())

        drink = self.backend.record_drink(METER_NAME, ticks=1, volume_ml=100, photo="foo")
        self.assertEqual("http://example.com:8000/d/{}".format(drink.id), drink.short_url())
        self.assertEqual(
            "http://example.com:8000/s/{}".format(drink.session.id), drink.session.short_url()
        )

        start = drink.session.start_time
        datepart = "{}/{}/{}".format(start.year, start.month, start.day)
        self.assertEqual(
            "http://example.com:8000/sessions/{}/{}".format(datepart, drink.session.id),
            drink.session.full_url(),
        )
