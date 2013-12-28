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

from . import models

DEFAULT_KEG_SIZE_GALLONS = 15.5
DEFAULT_KEG_SIZE_DESCRIPTION = "Full Keg (half barrel)"

METER_NAME_0 = 'kegboard.flow0'
METER_NAME_1 = 'kegboard.flow1'

def get_default_keg_size():
    volume = units.Quantity(DEFAULT_KEG_SIZE_GALLONS, units.UNITS.USGallon)
    volume_int = volume.Amount(in_units=units.RECORD_UNIT)
    return models.KegSize.objects.get_or_create(name=DEFAULT_KEG_SIZE_DESCRIPTION,
        volume_ml=volume_int)[0]

def db_is_installed():
    return models.KegbotSite.objects.all().count() > 0

class AlreadyInstalledError(Exception):
    """Thrown when database is already installed."""

def set_defaults(force=False, set_is_setup=False):
    """Creates a new site and sets defaults, returning that site."""
    if not force and db_is_installed():
        raise AlreadyInstalledError("Database is already installed.")

    site = models.KegbotSite.get()
    if set_is_setup and not site.is_setup:
        site.is_setup = True
        site.save()

    # KegTap defaults
    main_tap = models.KegTap(name='Main Tap', meter_name=METER_NAME_0)
    main_tap.save()
    secondary_tap = models.KegTap(name='Second Tap', meter_name=METER_NAME_1)
    secondary_tap.save()

    # brewer defaults
    unk_brewer = models.Brewer(name='Unknown Brewer')
    unk_brewer.save()

    # beerstyle defaults
    unk_style = models.BeerStyle(name='Unknown Style')
    unk_style.save()

    # beertype defaults
    unk_type = models.BeerType(name="Unknown Beer", brewer=unk_brewer, style=unk_style)
    unk_type.save()

    # KegSize defaults - from http://en.wikipedia.org/wiki/Keg#Size
    default_sizes = (
      (DEFAULT_KEG_SIZE_GALLONS, DEFAULT_KEG_SIZE_DESCRIPTION),
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
    return site
