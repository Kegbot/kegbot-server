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
        channel=0,
        status='online',
        description='Our first keg!',
        origcost=99.0,
    )

    self.user = models.User.objects.create(
        username='kb_tester',
    )

    self.user_profile = models.UserProfile.objects.create(
        user=self.user,
        gender='male',
        weight=150.0,
    )


  def tearDown(self):
    self.user_profile.delete()
    self.user.delete()
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
