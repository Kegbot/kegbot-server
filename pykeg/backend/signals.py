"""Custom signals from the Kegbot backend."""

from django.dispatch import Signal

user_created = Signal(providing_args=["user"])

tap_created = Signal(providing_args=["tap"])

auth_token_created = Signal(providing_args=["token"])

drink_recorded = Signal(providing_args=["drink"])

drink_canceled = Signal(providing_args=["drink"])

drink_assigned = Signal(providing_args=["drink", "previous_user"])

drink_adjusted = Signal(providing_args=["drink", "previous_volume"])

temperature_recorded = Signal(providing_args=["record"])

keg_created = Signal(providing_args=["keg"])

keg_attached = Signal(providing_args=["keg", "tap"])

keg_ended = Signal(providing_args=["keg"])
