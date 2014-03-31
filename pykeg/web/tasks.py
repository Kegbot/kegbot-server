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

from kegbot.util import util
from pykeg.plugin import util as plugin_util
from pykeg import notification
from pykeg.core import checkin
from pykeg.core import stats

from pykeg.celery import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def schedule_tasks(events):
    """Synchronously schedules tasks related to the given events."""
    for event in events:
        for plugin in plugin_util.get_plugins():
            plugin.handle_new_event(event)
    notification.handle_new_system_events(events)


@app.task
def handle_new_picture(picture_id):
    pass  # TODO(mikey): plugin support


@app.task
def ping():
    return True


@app.task(bind=True, default_retry_delay=60*60*1, max_retries=3)
def do_checkin(self):
    try:
        checkin.checkin()
    except checkin.CheckinError as exc:
        self.retry(exc=exc)

@app.task(queue='stats', expires=60*60)
def generate_stats_since(drink_id):
    logger.info('generate_stats_since {}'.format(drink_id))
    stats.rebuild_from_id(drink_id)
