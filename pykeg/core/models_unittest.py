"""Unittests for pykeg.core.models"""

import datetime
import unittest

from pykeg.core import models
from pykeg.core import units

class CoreModelsTestCase(unittest.TestCase):
  def setUp(self):
    self.brewer = models.Brewer.objects.create(
        name='Moonshine Beers',
        origin_country='USA',
        origin_state='Anystate',
        origin_city='Bathtub',
        distribution='retail',
        url='http://example.com/',
        comment='Pretty bad beers.',
    )

    self.beer_style = models.BeerStyle.objects.create(
        name='Porter',
    )

    self.beer_type = models.BeerType.objects.create(
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
        volume=self.keg_vol,
    )

    self.keg = models.Keg.objects.create(
        type=self.beer_type,
        size=self.keg_size,
        startdate=datetime.datetime(2000, 4, 1),
        enddate=datetime.datetime(2000, 5, 1),
        status='online',
        description='Our first keg!',
        origcost=99.0,
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
    self.assertEqual(self.keg.size.Volume().ConvertTo.Liter, 2.0)
    self.assertEqual(self.keg.type.brewer.name, "Moonshine Beers")

    self.assertEqual(self.keg.served_volume(), 0.0)
    self.assertEqual(self.keg.remaining_volume(), self.keg_vol)

  def testDrinkAccounting(self):
    vol = units.Quantity(1200)

    d = models.Drink.objects.create(
        ticks=vol.ConvertTo.KbMeterTick,
        volume=vol.ConvertTo.KbMeterTick,
        starttime=datetime.datetime.now(),
        endtime=datetime.datetime.now(),
        user=self.user,
        keg=self.keg,
        status='valid',
    )

    self.assertEqual(self.keg.served_volume(), d.volume)

  def testDrinkSessions(self):
    """ Checks for the UserDrinkingSession and DrinkingSessionGroup tables """
    u1 = self.user
    u2 = self.user2
    vol = units.Quantity(1200)

    drinks = {}
    base_time = datetime.datetime(2009,1,1,1,0,0)

    ticks = volume = vol.ConvertTo.KbMeterTick

    td_10m = datetime.timedelta(minutes=10)
    td_200m = datetime.timedelta(minutes=200)
    td_190m = td_200m - td_10m

    drinks[u1] = (
        # t=0
        models.Drink.objects.create(
          ticks=ticks, volume=volume, user=u1, keg=self.keg,
          starttime=base_time, endtime=base_time),
        # t=10
        models.Drink.objects.create(
          ticks=ticks, volume=volume, user=u1, keg=self.keg,
          starttime=base_time+td_10m, endtime=base_time+td_10m),
        # t=200
        models.Drink.objects.create(
          ticks=ticks, volume=volume, user=u1, keg=self.keg,
          starttime=base_time+td_200m, endtime=base_time+td_200m),
    )

    drinks[u2] = (
        # t=0
        models.Drink.objects.create(
          ticks=ticks, volume=volume, user=u2, keg=self.keg,
          starttime=base_time, endtime=base_time),
        # t=200
        models.Drink.objects.create(
          ticks=ticks, volume=volume, user=u2, keg=self.keg,
          starttime=base_time+td_200m, endtime=base_time+td_200m),
        # t=190
        models.Drink.objects.create(
          ticks=ticks, volume=volume, user=u2, keg=self.keg,
          starttime=base_time+td_190m, endtime=base_time+td_190m),
    )

    for u, ud in drinks.iteritems():
      for d in ud:
        models.UserDrinkingSessionAssignment.RecordDrink(d)

    u1_sessions = u1.userdrinkingsession_set.all()
    self.assertEqual(len(u1_sessions), 2)

    u2_sessions = u2.userdrinkingsession_set.all()
    self.assertEqual(len(u2_sessions), 2)

    # user1 session 1: should be 10 minutes long as created above
    u1_s1 = u1_sessions[0]
    self.assertEqual(u1_s1.starttime, base_time)
    self.assertEqual(u1_s1.starttime, drinks[u1][0].starttime)
    self.assertEqual(u1_s1.endtime, drinks[u1][1].endtime)
    self.assertEqual(u1_s1.endtime - u1_s1.starttime, td_10m)
    self.assertEqual(len(list(u1_s1.GetDrinks())), 2)

    # user1 session 2: at time 200, 1 drink
    u1_s2 = u1_sessions[1]
    self.assertEqual(u1_s2.starttime, base_time+td_200m)
    self.assertEqual(u1_s2.endtime, base_time+td_200m)
    self.assertEqual(len(list(u1_s2.GetDrinks())), 1)

    # user2 session2: drinks are added out of order to create this, ensure times
    # match
    u2_s2 = u2_sessions[1]
    self.assertEqual(u2_s2.starttime, base_time+td_190m)
    self.assertEqual(u2_s2.endtime, base_time+td_200m)
    self.assertEqual(len(list(u2_s2.GetDrinks())), 2)

    # Now check DrinkingSessionGroups were created correctly; there should be
    # two groups capturing all 4 sessions.
    all_groups = models.DrinkingSessionGroup.objects.all()
    self.assertEqual(len(all_groups), 2)

    self.assertEqual(all_groups[0].starttime, base_time)
    self.assertEqual(all_groups[0].endtime, base_time+td_10m)
    self.assertEqual(len(all_groups[0].GetSessions()), 2)

    self.assertEqual(all_groups[1].starttime, base_time+td_190m)
    self.assertEqual(all_groups[1].endtime, base_time+td_200m)
    self.assertEqual(len(all_groups[1].GetSessions()), 2)
