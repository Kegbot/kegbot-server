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

from . import models

METER_NAME_0 = 'kegboard.flow0'
METER_NAME_1 = 'kegboard.flow1'


def db_is_installed():
    return models.KegbotSite.objects.all().count() > 0


class AlreadyInstalledError(Exception):
    """Thrown when database is already installed."""


def set_defaults(force=False, set_is_setup=False, create_controller=False):
    """Creates a new site and sets defaults, returning that site."""
    if not force and db_is_installed():
        raise AlreadyInstalledError("Database is already installed.")

    site = models.KegbotSite.get()
    if set_is_setup and not site.is_setup:
        site.is_setup = True
        site.save()

    models.User.objects.create_user('guest')

    tap_0 = models.KegTap.objects.create(name='Main Tap')

    # Prior to 0.9.23, controller objects were created automatically.
    # This behavior is available for unittests which request it.
    if create_controller:
        tap_1 = models.KegTap.objects.create(name='Second Tap')
        controller = models.Controller.objects.create(name='kegboard')

        models.FlowMeter.objects.create(controller=controller, port_name='flow0',
            tap=tap_0)
        models.FlowMeter.objects.create(controller=controller, port_name='flow1',
            tap=tap_1)
        models.FlowToggle.objects.create(controller=controller, port_name='relay0',
            tap=tap_0)
        models.FlowToggle.objects.create(controller=controller, port_name='relay1',
            tap=tap_1)

    return site
