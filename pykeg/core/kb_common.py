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

"""System constants and defaults."""

# Where to look for local_settings.py
LOCAL_SETTINGS_SEARCH_DIRS = (
    '~/.kegbot/',
    '/etc/kegbot/',
    '/usr/local/etc/kegbot',
)

# SF800 default.
DEFAULT_TICKS_PER_ML = 5.4

# Minimum session size, in milliliters, to display
MIN_SESSION_VOLUME_DISPLAY_ML = 177  # 6 ounces

# Maximum time between consecutive drinks to be considered in the same 'session'
# (see UserDrinkingSession table)
DRINK_SESSION_TIME_MINUTES = 3 * 60

# Minimum and maximum thermo sensor readings (degrees C).
THERMO_SENSOR_RANGE = (-20.0, 80.0)

# Maximum number of readings to keep.
THERMO_SENSOR_HISTORY_MINUTES = 60 * 24

# Device names
AUTH_MODULE_CORE_ONEWIRE = 'core.onewire'
AUTH_MODULE_CORE_RFID = 'core.rfid'
AUTH_MODULE_CONTRIB_PHIDGET_RFID = AUTH_MODULE_CORE_RFID

# Auth modules whose token values should be interpreted as lower-case hex.
AUTH_MODULE_NAMES_HEX_VALUES = (AUTH_MODULE_CORE_ONEWIRE, AUTH_MODULE_CORE_RFID)

# Low volume threshold: 15% full
KEG_VOLUME_LOW_PERCENT = 0.15
