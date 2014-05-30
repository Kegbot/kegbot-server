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

"""Tasks for the Kegbot core."""

from pykeg.plugin import util as plugin_util
from pykeg import notification
from pykeg.core import stats
from pykeg.core import backup
from django.db import transaction

from pykeg.celery import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def schedule_tasks(events):
    """Synchronously schedules tasks related to the given events."""
    for plugin in plugin_util.get_plugins().values():
        try:
            plugin.handle_new_events(events)
        except Exception:
            logger.exception('Error dispatching events to plugin {}'.format(plugin.get_name()))
    notification.handle_new_system_events(events)


@app.task(name='build_stats', queue='stats', expires=60 * 60)
def build_stats(drink_id, rebuild_following):
    logger.info('build_stats drink_id={} rebuild_following={}'.format(
        drink_id, rebuild_following))
    with transaction.atomic():
        if rebuild_following:
            stats.rebuild_from_id(drink_id)
        else:
            stats.build_for_id(drink_id)


@app.task(name='build_backup', bind=True)
def build_backup(self):
    logger.info('build_backup')
    with transaction.atomic():
        backup.backup()
