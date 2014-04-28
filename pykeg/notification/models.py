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

"""Notification-related models."""

from django.db import models


class NotificationSettings(models.Model):
    """Stores a user's notification settings for a specific backend."""

    class Meta:
        unique_together = ('user', 'backend')

    user = models.ForeignKey('core.User',
        help_text='User for these settings.')
    backend = models.CharField(max_length=255,
        help_text='Notification backend (dotted path) for these settings.')
    keg_tapped = models.BooleanField(default=True,
        help_text='Sent when a keg is activated.')
    session_started = models.BooleanField(default=False,
        help_text='Sent when a new drinking session starts.')
    keg_volume_low = models.BooleanField(default=False,
        help_text='Sent when a keg becomes low.')
    keg_ended = models.BooleanField(default=False,
        help_text='Sent when a keg has been taken offline.')
