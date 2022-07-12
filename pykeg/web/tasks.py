"""Tasks for the Kegbot core."""

from celery.utils.log import get_task_logger
from django.db import transaction

from pykeg import notification
from pykeg.backup import backup
from pykeg.celery import app
from pykeg.core import stats
from pykeg.plugin import util as plugin_util

logger = get_task_logger(__name__)


def schedule_tasks(events):
    """Synchronously schedules tasks related to the given events."""
    for plugin in list(plugin_util.get_plugins().values()):
        try:
            plugin.handle_new_events(events)
        except Exception:
            logger.exception("Error dispatching events to plugin {}".format(plugin.get_name()))
    notification.handle_new_system_events(events)


@app.task(name="build_stats", queue="stats", expires=60 * 60)
def build_stats(drink_id, rebuild_following):
    logger.info("build_stats drink_id={} rebuild_following={}".format(drink_id, rebuild_following))
    with transaction.atomic():
        if rebuild_following:
            stats.rebuild_from_id(drink_id)
        else:
            stats.build_for_id(drink_id)


@app.task(name="build_backup", bind=True)
def build_backup(self):
    logger.info("build_backup")
    with transaction.atomic():
        backup.backup()
