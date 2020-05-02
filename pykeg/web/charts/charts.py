from past.builtins import cmp
import datetime

from django.utils import timezone
from pykeg.util import units
from pykeg.core.util import CtoF

from pykeg.core import models


class ChartError(Exception):
    """Base chart exception."""


def format_volume(volume_ml, chart_kwargs):
    metric_volumes = chart_kwargs.get("metric_volumes", False)
    if metric_volumes:
        return volume_ml / 1000.0, "L"
    else:
        return units.Quantity(volume_ml).InPints(), "pints"


def format_temperature(temp_c, chart_kwargs):
    use_c = chart_kwargs.get("temperature_units", None) == "c"
    if use_c:
        return temp_c
    else:
        return CtoF(temp_c)


def chart_temp_sensor(sensor, *args, **kwargs):
    """ Shows a simple line plot of a specific temperature sensor.

    Syntax:
      {% chart temp_sensor <sensorname> width height %}
    Args:
      sensorname - the nice_name of a ThermoSensor
    """
    if not isinstance(sensor, models.ThermoSensor):
        raise ChartError("Bad sensor given")

    hours = 6
    now = timezone.now()
    start = now - (datetime.timedelta(hours=hours))
    start = start - (datetime.timedelta(seconds=start.second))

    points = sensor.thermolog_set.filter(time__gte=start).order_by("time")

    curr = start
    temps = []
    have_temps = False
    for point in points:
        temp = format_temperature(point.temp, kwargs)
        while curr <= point.time:
            curr += datetime.timedelta(minutes=1)
            if curr < point.time:
                temps.append(None)
            else:
                temps.append(temp)
                have_temps = True

    if not have_temps:
        raise ChartError("Not enough data")

    res = {
        "series": [{"data": temps, "marker": {"enabled": False,},},],
        "tooltip": {"enabled": True,},
        "xAxis": {
            "categories": ["Temperature"],
            "labels": {"enabled": False,},
            "tickInterval": 60,
        },
        "yAxis": {"labels": {"enabled": True,}, "tickInterval": 1,},
    }
    return res


def chart_volume_by_weekday(stats, *args, **kwargs):
    """ Shows a histogram of volume by day of the week.

    Syntax:
      {% chart volume_by_weekday <stats> width height %}
    Args:
      stats - a stats object containing volume_by_day_of_week
    """
    volmap = [0] * 7
    vols = stats.get("volume_by_day_of_week", {})
    if not volmap:
        raise ChartError("Daily volumes unavailable")

    for weekday, volume_ml in list(vols.items()):
        volmap[int(weekday)] += format_volume(volume_ml, kwargs)[0]
    return _weekday_chart_common(volmap)


def chart_sessions_by_weekday(stats, *args, **kwargs):
    data = stats.get("volume_by_day_of_week", {})
    weekdays = [0] * 7
    for weekday, volume_ml in list(data.items()):
        weekdays[int(weekday)] += format_volume(volume_ml, kwargs)[0]
    return _weekday_chart_common(weekdays)


def chart_sessions_by_volume(stats, *args, **kwargs):
    buckets = [0] * 6
    labels = ["<1", "1.0-1.9", "2.0-2.9", "3.0-3.9", "4.0-4.9", "5+"]
    volmap = stats.get("volume_by_session", {})
    for session_volume in list(volmap.values()):
        volume = round(format_volume(session_volume, kwargs)[0], 1)
        intval = int(volume)
        if intval >= len(buckets):
            buckets[-1] += 1
        else:
            buckets[intval] += 1

    res = {
        "xAxis": {"categories": labels,},
        "series": [{"data": buckets},],
        "yAxis": {"min": 0,},
        "chart": {"defaultSeriesType": "column",},
    }
    return res


def chart_users_by_volume(stats, *args, **kwargs):
    vols = stats.get("volume_by_drinker")
    if not vols:
        raise ChartError("no data")

    data = []
    for username, volume in list(vols.items()):
        if not username:
            username = "Guest"
        volume, units = format_volume(volume, kwargs)
        label = "<b>%s</b> (%.1f %s)" % (username, volume, units)
        data.append((label, volume))

    def _sort_vol_desc(a, b):
        return cmp(b[1], a[1])

    other_vol = 0
    data.sort(key=lambda item: item[1])
    for username, pints in data[10:]:
        other_vol += pints
    data = data[:10]
    data.reverse()

    if other_vol:
        label = "<b>%s</b> (%.1f)" % ("all others", other_vol)
        data.append((label, other_vol))

    res = {
        "series": [{"type": "pie", "name": "Drinkers by Volume", "data": data,}],
        "yAxis": {"min": 0,},
        "chart": {"defaultSeriesType": "column",},
        "tooltip": {"enabled": False,},
    }
    return res


def _weekday_chart_common(vals):
    labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # convert from 0=Monday to 0=Sunday
    # vals.insert(0, vals.pop(-1))

    res = {
        "xAxis": {"categories": labels,},
        "yAxis": {"min": 0,},
        "series": [{"data": vals},],
        "tooltip": {"enabled": False,},
        "chart": {"defaultSeriesType": "column",},
    }
    return res
