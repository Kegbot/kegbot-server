"""Unittests for pykeg.core.models"""

import datetime
import unittest

from pykeg.core import backend
from pykeg.core import kb_common
from pykeg.core import models
from pykeg.core import units

from pykeg.beerdb import models as bdb_models

class CoreModelsTestCase(unittest.TestCase):
  def setUp(self):
    models.KegbotSite.objects.filter(name='default').delete()
    self.site, created = models.KegbotSite.objects.get_or_create(name='default')
    self.backend = backend.KegbotBackend(site=self.site)
    self.brewer = bdb_models.Brewer.objects.create(
        name='Moonshine Beers',
        country='USA',
        origin_state='Anystate',
        origin_city='Bathtub',
        production='retail',
        url='http://example.com/',
        description='Pretty bad beers.',
    )

    self.beer_style = bdb_models.BeerStyle.objects.create(
        name='Porter',
    )

    self.beer_type = bdb_models.BeerType.objects.create(
        name='Moonshine Porter',
        brewer=self.brewer,
        style=self.beer_style,
        calories_oz=3.0,
        carbs_oz=10.0,
        abv=0.05,
    )

    self.keg_vol = units.UnitConverter.Convert(2.0, units.UNITS.Liter,
                                               units.RECORD_UNIT)
    self.keg_size = models.KegSize.objects.create(
        name='Tiny Keg',
        volume_ml=self.keg_vol,
    )

    self.keg = models.Keg.objects.create(
        site=self.site,
        type=self.beer_type,
        size=self.keg_size,
        startdate=datetime.datetime(2000, 4, 1),
        enddate=datetime.datetime(2000, 5, 1),
        status='online',
        description='Our first keg!',
        origcost=99.0,
    )

    self.tap = models.KegTap.objects.create(
        site=self.site,
        name='Test Tap',
        meter_name='test',
        ml_per_tick=(1000.0/2200.0),
        current_keg=self.keg,
    )

    self.user = models.User.objects.create(
        username='kb_tester',
    )

    self.user2 = models.User.objects.create(
        username='kb_tester2',
    )

  def tearDown(self):
    self.user.delete()
    self.user2.delete()
    self.keg.delete()
    del self.keg_vol
    self.beer_type.delete()
    self.beer_style.delete()
    self.brewer.delete()

  def testKegStuff(self):
    """Test basic keg relations that should always work."""
    self.assertEqual(self.keg.size.volume_ml,
        units.Quantity(2.0, units.UNITS.Liter).InMilliliters())
    self.assertEqual(self.keg.type.brewer.name, "Moonshine Beers")

    self.assertEqual(self.keg.served_volume(), 0.0)
    self.assertEqual(self.keg.remaining_volume(), self.keg_vol)

  def testDrinkAccounting(self):
    vol = units.Quantity(1200)

    d = self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=self.user.username,
    )

    print d

    self.assertEqual(self.keg.served_volume(), d.volume_ml)

  def testDrinkSessions(self):
    """ Checks for the DrinkingSession records. """
    u1 = self.user
    u2 = self.user2
    vol = units.Quantity(1200)

    drinks = {}
    base_time = datetime.datetime(2009,1,1,1,0,0)

    ticks = volume = vol.InKbMeterTicks()

    td_10m = datetime.timedelta(minutes=10)
    td_200m = datetime.timedelta(minutes=200)
    td_190m = td_200m - td_10m

    self.assertEqual(models.Drink.objects.all().count(), 0)
    self.assertEqual(models.DrinkingSession.objects.all().count(), 0)

    ### User 1
    # t=0
    print self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u1.username,
        pour_time=base_time,
    )
    # t=10
    print self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u1.username,
        pour_time=base_time+td_10m,
    )
    # t=200
    print self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u1.username,
        pour_time=base_time+td_200m,
    )
    drinks_u1 = u1.drinks.all().order_by('starttime')


    ### User 2
    # t=0
    print self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u2.username,
        pour_time=base_time,
    )
    # t=200
    print self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u2.username,
        pour_time=base_time+td_200m,
    )
    # t=190
    print self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u2.username,
        pour_time=base_time+td_190m,
    )
    drinks_u2 = u2.drinks.all().order_by('starttime')

    u1_chunks = u1.session_chunks.all().order_by('starttime')
    self.assertEqual(len(u1_chunks), 2)

    u2_chunks = u2.session_chunks.all().order_by('starttime')
    self.assertEqual(len(u2_chunks), 2)

    s1, s2 = models.DrinkingSession.objects.all().order_by('starttime')[:2]

    SESSION_DELTA = datetime.timedelta(minutes=kb_common.DRINK_SESSION_TIME_MINUTES)

    # session 1: should be 10 minutes long as created above
    self.assertEqual(s1.starttime, drinks_u1[0].starttime)
    self.assertEqual(s1.endtime, drinks_u1[1].starttime)
    self.assertEqual(s1.drinks.valid().filter(user=u1).count(), 2)
    self.assertEqual(s1.drinks.valid().filter(user=u2).count(), 1)

    # session 2: at time 200, 1 drink
    self.assertEqual(s2.starttime, base_time + td_190m)
    self.assertEqual(s2.endtime, base_time + td_200m)
    self.assertEqual(s2.drinks.valid().filter(user=u1).count(), 1)
    self.assertEqual(s2.drinks.valid().filter(user=u2).count(), 2)

    # user2 session2: drinks are added out of order to create this, ensure times
    # match
    u2_c2 = u2_chunks[1]
    self.assertEqual(u2_c2.starttime, base_time+td_190m)
    self.assertEqual(u2_c2.endtime, base_time+td_200m)

    # Now check DrinkingSessions were created correctly; there should be
    # two groups capturing all 4 sessions.
    all_groups = models.DrinkingSession.objects.all().order_by('starttime')
    self.assertEqual(len(all_groups), 2)

    self.assertEqual(all_groups[0].starttime, base_time)
    self.assertEqual(all_groups[0].endtime, base_time+td_10m)
    self.assertEqual(all_groups[0].user_chunks.all().count(), 2)

    self.assertEqual(all_groups[1].starttime, base_time+td_190m)
    self.assertEqual(all_groups[1].endtime, base_time+td_200m)
    self.assertEqual(all_groups[1].user_chunks.all().count(), 2)
