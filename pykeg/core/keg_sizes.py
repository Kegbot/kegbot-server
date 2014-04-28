# Copyright 2014 Bevbot LLC, All Rights Reserved
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

"""Constants about physical keg shell."""

# Most common shell sizes, from smalles to largest.
CORNY = 'corny'
SIXTH_BARREL = 'sixth'
EURO_HALF_BARREL = 'euro-half'
QUARTER_BARREL = 'quarter'
EURO = 'euro'
HALF_BARREL = 'half-barrel'
OTHER = 'other'

VOLUMES_ML = {
    CORNY: 18927.1,
    SIXTH_BARREL: 19570.6,
    EURO_HALF_BARREL: 50000.0,
    QUARTER_BARREL: 29336.9,
    EURO: 100000.0,
    HALF_BARREL: 58673.9,
    OTHER: 0.0
}

DESCRIPTIONS = {
    CORNY: 'Corny Keg (5 gal)',
    SIXTH_BARREL: 'Sixth Barrel (5.17 gal)',
    EURO_HALF_BARREL: 'European Half Barrel (50 L)',
    QUARTER_BARREL: 'Quarter Barrel (7.75 gal)',
    EURO: 'European Full Barrel (100 L)',
    HALF_BARREL: 'Half Barrel (15.5 gal)',
    OTHER: 'Other',
}

CHOICES = [(x, DESCRIPTIONS[x]) for x in reversed(sorted(VOLUMES_ML, key=VOLUMES_ML.get))]


def find_closest_keg_size(volume_ml, tolerance_ml=100.0):
    """Returns the nearest fuzzy match name within tolerance_ml.

    If no match is found, OTHER is returned.
    """
    for size_name, size_volume_ml in VOLUMES_ML.iteritems():
        diff = abs(volume_ml - size_volume_ml)
        if diff <= tolerance_ml:
            return size_name
    return OTHER


def get_description(keg_type):
    return DESCRIPTIONS.get(keg_type, 'Unknown')
