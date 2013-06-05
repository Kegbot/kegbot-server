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

"""Unittests for backend"""

from django.test import TestCase
from pykeg.core import models
from pykeg.core import defaults

from . import backend

TAP_NAME = 'kegboard.flow0'
FAKE_BEER_NAME = 'Testy Beer'
FAKE_BREWER_NAME = 'Unittest Brewery'
FAKE_BEER_STYLE = 'Test-Driven Pale Ale'

### Helper methods

class BaseApiTestCase(TestCase):
	def setUp(self):
		self.backend = backend.KegbotBackend()
		defaults.set_defaults(set_is_setup=True)

	def test_drink_management(self):
		"""Test adding drinks."""
		tap = models.KegTap.objects.get(meter_name=TAP_NAME)
		keg = self.backend.StartKeg(TAP_NAME, beer_name=FAKE_BEER_NAME,
				brewer_name=FAKE_BREWER_NAME, style_name=FAKE_BEER_STYLE)
		self.assertIsNotNone(keg)

		self.assertEquals(0, keg.served_volume())
		drink = self.backend.RecordDrink(TAP_NAME, ticks=2200)
		self.assertIsNotNone(drink)
		self.assertEquals(2200, drink.ticks)
		self.assertAlmostEqual(1000.0, drink.volume_ml, places=3)
		self.assertAlmostEqual(1000.0, keg.served_volume(), places=3)
		self.assertEquals('', drink.shout)
		self.assertEquals(0, drink.duration)

		drink = self.backend.RecordDrink(TAP_NAME, ticks=1100)
		self.assertIsNotNone(drink)
		self.assertEquals(1100, drink.ticks)
		self.assertAlmostEqual(500.0, drink.volume_ml, places=3)
		self.assertAlmostEqual(1500.0, keg.served_volume(), places=3)

		# Add with volume, taking precedence over ticks.
		drink = self.backend.RecordDrink(TAP_NAME, ticks=1100, volume_ml=1)
		self.assertIsNotNone(drink)
		self.assertEquals(1100, drink.ticks)
		self.assertAlmostEqual(1.0, drink.volume_ml, places=3)
		self.assertAlmostEqual(1501.0, keg.served_volume(), places=3)

		# Add with a user.
		user = models.User.objects.create(username='testy')
		drink = self.backend.RecordDrink(TAP_NAME, ticks=2200, username=user.username)
		self.assertIsNotNone(drink)
		self.assertEquals(user, drink.user)

	def test_drink_cancel(self):
		"""Tests cancelling drinks."""
		tap = models.KegTap.objects.get(meter_name=TAP_NAME)
		keg = self.backend.StartKeg(TAP_NAME, beer_name=FAKE_BEER_NAME,
				brewer_name=FAKE_BREWER_NAME, style_name=FAKE_BEER_STYLE)
		self.assertIsNotNone(keg)
		self.assertEquals(0, keg.served_volume())

		for i in xrange(10):
			d = self.backend.RecordDrink(tap_name=TAP_NAME, ticks=1, volume_ml=100)

		drinks = list(models.Drink.objects.all().order_by('id'))
		self.assertEquals(10, len(drinks))
		self.assertAlmostEqual(1000.0, keg.served_volume(), places=3)

		cancel_drink = drinks[-1]
		session = cancel_drink.session
		self.assertAlmostEqual(session.GetStats().total_volume_ml, 1000.0, places=3)

		self.backend.CancelDrink(drinks[-1])
		drinks = list(models.Drink.objects.all().order_by('id'))
		self.assertEquals(9, len(drinks))
		self.assertAlmostEqual(900.0, keg.served_volume(), places=3)
		session = models.DrinkingSession.objects.get(id=session.id)
		self.assertAlmostEqual(session.GetStats().total_volume_ml, 900.0, places=3)

		spilled_drink = drinks[-1]
		keg = models.Keg.objects.all()[0]
		self.assertEquals(0, keg.spilled_ml)
		self.backend.CancelDrink(drinks[-1], spilled=True)
		keg = models.Keg.objects.all()[0]
		drinks = list(models.Drink.objects.all().order_by('id'))
		self.assertEquals(8, len(drinks))
		self.assertAlmostEqual(900.0, keg.served_volume(), places=3)
		self.assertAlmostEqual(100.0, keg.spilled_ml, places=3)

	def test_keg_management(self):
		"""Tests adding and removing kegs."""
		tap = models.KegTap.objects.get(meter_name=TAP_NAME)
		self.assertFalse(tap.is_active(), "Tap is already active.")

		# No beer types yet.
		qs = models.BeerType.objects.filter(name=FAKE_BEER_NAME)
		self.assertEquals(len(qs), 0, "BeerType already exists")

		# Tap the keg.
		keg = self.backend.StartKeg(TAP_NAME, beer_name=FAKE_BEER_NAME,
				brewer_name=FAKE_BREWER_NAME, style_name=FAKE_BEER_STYLE)
		self.assertIsNotNone(keg)
		self.assertTrue(keg.online)

		self.assertEquals(keg.current_tap, tap, "Tap did not become active.")
		tap = keg.current_tap
		self.assertTrue(keg.current_tap.is_active())

		# Check that the beer type was created.
		qs = models.BeerType.objects.filter(name=FAKE_BEER_NAME)
		self.assertEquals(len(qs), 1, "Expected a single new BeerType.")
		beer_type = qs[0]
		brewer = beer_type.brewer
		style = beer_type.style
		self.assertEquals(brewer.name, FAKE_BREWER_NAME)
		self.assertEquals(style.name, FAKE_BEER_STYLE)

		# Now activate a new keg.
		keg_id = keg.id
		keg = self.backend.EndKeg(tap)
		tap = models.KegTap.objects.get(meter_name=TAP_NAME)
		self.assertFalse(tap.is_active())
		self.assertFalse(keg.online)

		new_keg = self.backend.StartKeg(TAP_NAME, beer_type=beer_type)
		self.assertIsNotNone(new_keg)
		self.assertNotEquals(new_keg, keg)

		# Ensure the beer type was reused.
		self.assertEquals(new_keg.type, beer_type)

		# Deactivate, and activate a new keg again by name.
		self.backend.EndKeg(tap.meter_name)
		new_keg_2 = self.backend.StartKeg(TAP_NAME, beer_name='Other Beer',
				brewer_name=FAKE_BREWER_NAME, style_name=FAKE_BEER_STYLE)
		self.assertEquals(new_keg_2.type.brewer, keg.type.brewer)
		self.assertEquals(new_keg_2.type.style, keg.type.style)
		self.assertNotEquals(new_keg_2.type, keg.type)

		# New brewer, identical beer name == new beer type.
		self.backend.EndKeg(tap.meter_name)
		new_keg_3 = self.backend.StartKeg(TAP_NAME, beer_name=FAKE_BEER_NAME,
				brewer_name='Other Brewer', style_name=FAKE_BEER_STYLE)
		self.assertNotEquals(new_keg_3.type.brewer, keg.type.brewer)
		self.assertEquals(new_keg_3.type.name, keg.type.name)
		self.assertNotEquals(new_keg_3.type, keg.type)
