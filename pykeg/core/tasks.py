"""Tasks for the Kegbot core."""

import logging

from django.db import transaction
from django_rq import job

from pykeg import notification
from pykeg.backup import backup
from pykeg.plugin import util as plugin_util

from . import stats

logger = logging.getLogger(__name__)


def schedule_tasks(events):
    """Synchronously schedules tasks related to the given events."""
    for plugin in list(plugin_util.get_plugins().values()):
        try:
            plugin.handle_new_events(events)
        except Exception:
            logger.exception("Error dispatching events to plugin {}".format(plugin.get_name()))
    notification.handle_new_system_events(events)


@job("stats")
def build_stats(drink_id, rebuild_following):
    logger.info("build_stats drink_id={} rebuild_following={}".format(drink_id, rebuild_following))
    with transaction.atomic():
        if rebuild_following:
            stats.rebuild_from_id(drink_id)
        else:
            stats.build_for_id(drink_id)


@job
def build_backup():
    logger.info("build_backup")
    with transaction.atomic():
        backup.backup()
