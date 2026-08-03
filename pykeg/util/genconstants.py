"""Builds the constants object shared with the frontend.

The `print_constants` management command writes this to a TypeScript file
that is baked into the frontend build; regenerate it whenever any of the
source constants change.
"""

from pykeg.core import keg_sizes, models
from pykeg.core.timezones import timezone_choices


def sort_dict_by_keys(d):
    return dict(sorted(d.items()))


def genconstants():
    """Returns the object written to `web-ui/lib/shared-constants.ts`.

    Note on sorting: most values are sorted by key to keep regeneration
    diffs minimal; javascript consumers re-sort for presentation where
    ordering matters (e.g. keg types by volume, via KEG_VOLUMES_ML).
    """
    return {
        "BEVERAGE_TYPES": dict(models.Beverage.TYPES),
        "EVENT_KINDS": dict(models.SystemEvent.KINDS),
        "KEG_STATUSES": dict(models.Keg.STATUS_CHOICES),
        "KEG_STATUS_AVAILABLE": models.Keg.STATUS_AVAILABLE,
        "KEG_STATUS_FINISHED": models.Keg.STATUS_FINISHED,
        "KEG_STATUS_ON_TAP": models.Keg.STATUS_ON_TAP,
        "KEG_TYPES": sort_dict_by_keys(keg_sizes.DESCRIPTIONS),
        "KEG_TYPE_OTHER": keg_sizes.OTHER,
        "KEG_VOLUMES_ML": sort_dict_by_keys(keg_sizes.VOLUMES_ML),
        "PRIVACY_CHOICES": dict(models.KegbotSite.PRIVACY_CHOICES),
        "REGISTRATION_MODE_CHOICES": dict(models.KegbotSite.REGISTRATION_MODE_CHOICES),
        "TEMPERATURE_DISPLAY_UNITS_CHOICES": dict(
            models.KegbotSite.TEMPERATURE_DISPLAY_UNITS_CHOICES
        ),
        "TIMEZONES": [zone for zone, _ in timezone_choices()],
        "VOLUME_DISPLAY_UNITS_CHOICES": dict(models.KegbotSite.VOLUME_DISPLAY_UNITS_CHOICES),
    }
