"""Custom signals from the Kegbot backend."""

from django.dispatch import Signal

user_created = Signal()

tap_created = Signal()

auth_token_created = Signal()

drink_recorded = Signal()

drink_canceled = Signal()

drink_assigned = Signal()

drink_adjusted = Signal()

temperature_recorded = Signal()

keg_created = Signal()

keg_attached = Signal()

keg_ended = Signal()

keg_deleted = Signal()

events_created = Signal()
