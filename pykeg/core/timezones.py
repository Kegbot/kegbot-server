"""Time zone choices for the KegbotSite.timezone field."""

from zoneinfo import available_timezones


def timezone_choices():
    """Returns (value, label) choices for every region/city zone, plus UTC.

    Passed as a callable so migrations reference this function rather than
    a snapshot of the list; tzdata updates never require a new migration.
    """
    zones = {z for z in available_timezones() if "/" in z and not z.startswith("Etc/")}
    zones.add("UTC")
    return [(z, z) for z in sorted(zones)]
