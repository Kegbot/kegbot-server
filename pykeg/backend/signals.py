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

"""Custom signals from the Kegbot backend."""

from django.dispatch import Signal

user_created = Signal(providing_args=['user'])

tap_created = Signal(providing_args=['tap'])

auth_token_created = Signal(providing_args=['token'])

drink_recorded = Signal(providing_args=['drink'])

drink_canceled = Signal(providing_args=['drink'])

drink_assigned = Signal(providing_args=['drink', 'previous_user'])

drink_adjusted = Signal(providing_args=['drink', 'previous_volume'])

temperature_recorded = Signal(providing_args=['record'])

keg_created = Signal(providing_args=['keg'])

keg_attached = Signal(providing_args=['keg', 'tap'])

keg_ended = Signal(providing_args=['keg'])
