# Copyright 2013 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Unittests for pykeg.core.models"""

import datetime

from django.conf import settings
from django.utils import timezone
from django.test import TestCase

from . import backend
from . import kb_common
from . import models
from .testutils import make_datetime

from kegbot.util import units

class CoreModelsTestCase(TestCase):
  def setUp(self):
    models.KegbotSite.get()  # create the site
    self.backend = backend.KegbotBackend()
    self.brewer = models.Brewer.objects.create(
        name='Moonshine Beers',
        country='USA',
        origin_state='Anystate',
        origin_city='Bathtub',
        production='retail',
        url='http://example.com/',
        description='Pretty bad beers.',
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
        volume_ml=self.keg_vol,
    )

    self.keg = models.Keg.objects.create(
        type=self.beer_type,
        size=self.keg_size,
        start_time=make_datetime(2000, 4, 1),
        end_time=make_datetime(2000, 5, 1),
        description='Our first keg!',
    )

    self.tap = models.KegTap.objects.create(
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
    base_time = make_datetime(2009,1,1,1,0,0)

    ticks = volume = vol.InKbMeterTicks()

    td_10m = datetime.timedelta(minutes=10)
    td_400m = datetime.timedelta(minutes=400)
    td_390m = td_400m - td_10m

    self.assertEqual(models.Drink.objects.all().count(), 0)
    self.assertEqual(models.DrinkingSession.objects.all().count(), 0)

    # u=1 t=0
    self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u1.username,
        pour_time=base_time,
    )
    # u=2 t=0
    self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u2.username,
        pour_time=base_time,
    )

    # u=1 t=10
    self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u1.username,
        pour_time=base_time+td_10m,
    )

    # u=1 t=400
    self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u1.username,
        pour_time=base_time+td_400m,
    )

    # u=2 t=490
    self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u2.username,
        pour_time=base_time+td_390m,
    )

    # u=2 t=400
    self.backend.RecordDrink(tap_name=self.tap.meter_name,
        ticks=1200,
        username=u2.username,
        pour_time=base_time+td_400m,
    )

    drinks_u1 = u1.drinks.all().order_by('time')
    drinks_u2 = u2.drinks.all().order_by('time')

    u1_chunks = u1.session_chunks.all().order_by('start_time')
    self.assertEqual(len(u1_chunks), 2)

    u2_chunks = u2.session_chunks.all().order_by('start_time')
    self.assertEqual(len(u2_chunks), 2)

    s1, s2 = models.DrinkingSession.objects.all().order_by('start_time')[:2]

    SESSION_DELTA = datetime.timedelta(minutes=kb_common.DRINK_SESSION_TIME_MINUTES)

    # session 1: should be 10 minutes long as created above
    self.assertEqual(s1.start_time, drinks_u1[0].time)
    self.assertEqual(s1.end_time, drinks_u1[0].time + td_10m + SESSION_DELTA)
    self.assertEqual(s1.drinks.all().filter(user=u1).count(), 2)
    self.assertEqual(s1.drinks.all().filter(user=u2).count(), 1)

    # session 2: at time 200, 1 drink
    self.assertEqual(s2.start_time, base_time + td_390m)
    self.assertEqual(s2.end_time, base_time + td_400m + SESSION_DELTA)
    self.assertEqual(s2.drinks.all().filter(user=u1).count(), 1)
    self.assertEqual(s2.drinks.all().filter(user=u2).count(), 2)

    # user2 session2: drinks are added out of order to create this, ensure times
    # match
    u2_c2 = u2_chunks[1]
    self.assertEqual(u2_c2.start_time, base_time + td_390m)
    self.assertEqual(u2_c2.end_time, base_time + td_400m + SESSION_DELTA)

    # Now check DrinkingSessions were created correctly; there should be
    # two groups capturing all 4 sessions.
    all_groups = models.DrinkingSession.objects.all().order_by('start_time')
    self.assertEqual(len(all_groups), 2)

    self.assertEqual(all_groups[0].start_time, base_time)
    self.assertEqual(all_groups[0].end_time, base_time + td_10m + SESSION_DELTA)
    self.assertEqual(all_groups[0].user_chunks.all().count(), 2)

    self.assertEqual(all_groups[1].start_time, base_time + td_390m)
    self.assertEqual(all_groups[1].end_time, base_time + td_400m + SESSION_DELTA)
    self.assertEqual(all_groups[1].user_chunks.all().count(), 2)
