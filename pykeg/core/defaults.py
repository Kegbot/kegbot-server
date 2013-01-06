# Copyright 2003-2009 Mike Wakerly <opensource@hoho.com>
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

import uuid

from kegbot.util import units

from pykeg.core.backend.django import KegbotBackend
from pykeg.core import models

from pykeg.beerdb import models as bdb

def db_is_installed():
  return models.KegbotSite.objects.all() > 0

def set_defaults(force=False):
  """ default values (contents may change with schema) """
  if not force and db_is_installed():
    raise RuntimeError, "Database is already installed."

  site = models.KegbotSite.objects.create(name='default')

  # KegTap defaults
  main_tap = models.KegTap(site=site, name='Main Tap', meter_name='kegboard.flow0')
  main_tap.save()
  secondary_tap = models.KegTap(site=site, name='Second Tap', meter_name='kegboard.flow1')
  secondary_tap.save()

  # brewer defaults
  unk_brewer = bdb.Brewer(name='Unknown Brewer', id=uuid.uuid4())
  unk_brewer.save()

  # beerstyle defaults
  unk_style = bdb.BeerStyle(name='Unknown Style', id=uuid.uuid4())
  unk_style.save()

  # beertype defaults
  unk_type = bdb.BeerType(name="Unknown Beer", id=uuid.uuid4(), brewer=unk_brewer, style=unk_style)
  unk_type.save()

  # KegSize defaults - from http://en.wikipedia.org/wiki/Keg#Size
  default_sizes = (
    (15.5, "Full Keg (half barrel)"),
    (13.2, "Import Keg (European barrel)"),
    (7.75, "Pony Keg (quarter barrel)"),
    (6.6, "European Half Barrel"),
    (5.23, "Sixth Barrel (torpedo keg)"),
    (5.0, "Corny Keg"),
    (1.0, "Mini Keg"),
  )
  for gallons, description in default_sizes:
    volume = units.Quantity(gallons, units.UNITS.USGallon)
    volume_int = volume.Amount(in_units=units.RECORD_UNIT)

    ks = models.KegSize(
      name=description,
      volume_ml=volume_int,
    )
    ks.save()
