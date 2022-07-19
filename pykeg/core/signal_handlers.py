from django.dispatch import receiver

from . import signals, tasks


@receiver(signals.drink_recorded)
def on_drink_recorded(sender, **kwargs):
    """Build stats when a drink is created."""
    drink = kwargs["drink"]
    tasks.build_stats.delay(drink_id=drink.id, rebuild_following=False)


@receiver(signals.drink_assigned)
@receiver(signals.drink_adjusted)
@receiver(signals.drink_canceled)
def on_drink_changed(sender, **kwargs):
    """Rebuild stats when a drink is changed or (re-)assigned."""
    drink_id = kwargs["drink_id"]
    tasks.build_stats.delay(drink_id=drink_id, rebuild_following=True)


@receiver(signals.keg_deleted)
def on_keg_deleted(sender, **kwargs):
    """Rebuild stats when a keg is deleted."""
    first_deleted_drink_id = kwargs["first_deleted_drink_id"]
    if first_deleted_drink_id:
        tasks.build_stats.delay(drink_id=first_deleted_drink_id, rebuild_following=True)


@receiver(signals.events_created)
def on_events_created(sender, **kwargs):
    """Send events to plugins."""
    events = kwargs["events"]
    tasks.schedule_tasks(events)
