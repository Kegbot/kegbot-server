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

"""Base notification module."""


class BaseNotificationBackend:
    """Base class for notification backend implementations."""

    def notify(self, event, user):
        """Sends a single notification.

        Args:
            event: the SystemEvent triggering a notification.
            user: the user who should receive the notification.

        Returns:
            True on success, False otherwise.
        """
        raise NotImplementedError('Subclasses must override notify() method')
