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

import datetime

from django.utils import timezone
from kegbot.util import units

from pykeg.core import models

class ChartError(Exception):
    """Base chart exception."""


def to_pints(volume):
    return float(units.Quantity(volume).InPints())


def chart_temp_sensor(sensor):
    """ Shows a simple line plot of a specific temperature sensor.

    Syntax:
      {% chart temp_sensor <sensorname> width height %}
    Args:
      sensorname - the nice_name of a ThermoSensor
    """
    if not isinstance(sensor, models.ThermoSensor):
        raise ChartError('Bad sensor given')

    hours = 6
    now = timezone.now()
    start = now - (datetime.timedelta(hours=hours))
    start = start - (datetime.timedelta(seconds=start.second))

    points = sensor.thermolog_set.filter(time__gte=start).order_by('time')

    curr = start
    temps = []
    have_temps = False
    for point in points:
        while curr <= point.time:
            curr += datetime.timedelta(minutes=1)
            if curr < point.time:
                temps.append(None)
            else:
                temps.append(point.temp)
                have_temps = True

    if not have_temps:
        raise ChartError('Not enough data')

    res = {
      'series': [
        {
          'data': temps,
          'marker': {
            'enabled': False,
          },
        },
      ],
      'tooltip': {
        'enabled': False,
      },
      'xAxis': {
        'categories': ['Temperature'],
        'labels': {
          'enabled': False,
        },
        'tickInterval': 0,
      },
      'yAxis': {
        'labels': {
          'enabled': False,
        },
        'tickInterval': 1,
      },
    }
    return res

def chart_volume_by_weekday(stats):
    """ Shows a histogram of volume by day of the week.

    Syntax:
      {% chart volume_by_weekday <stats> width height %}
    Args:
      stats - a stats object containing volume_by_day_of_week
    """
    volmap = [0] * 7
    vols = stats.get('volume_by_day_of_week', {})
    if not volmap:
        raise ChartError('Daily volumes unavailable')

    for weekday, vol in vols.iteritems():
        volmap[int(weekday)] += to_pints(vol)
    return _weekday_chart_common(volmap)

def chart_sessions_by_weekday(stats):
    data = stats.get('volume_by_day_of_week', {})
    weekdays = [0] * 7
    for weekday, volume_ml in data.iteritems():
        weekdays[int(weekday)] += to_pints(volume_ml)
    return _weekday_chart_common(weekdays)

def chart_sessions_by_volume(stats):
    buckets = [0]*6
    labels = [
      '<1',
      '1.0-1.9',
      '2.0-2.9',
      '3.0-3.9',
      '4.0-4.9',
      '5+'
    ]
    volmap = stats.get('volume_by_session', {})
    for session_volume in volmap.values():
        pints = round(to_pints(session_volume), 1)
        intval = int(pints)
        if intval >= len(buckets):
            buckets[-1] += 1
        else:
            buckets[intval] += 1

    res = {
      'xAxis': {
        'categories': labels,
      },
      'series': [
        {'data': buckets},
      ],
      'yAxis': {
        'min': 0,
      },
      'chart': {
        'defaultSeriesType': 'column',
      }
    }
    return res

def chart_users_by_volume(stats):
    vols = stats.get('volume_by_drinker')
    if not vols:
        raise ChartError('no data')

    data = []
    for username, volume in vols.iteritems():
        if not username:
          username = 'Guest'
        pints = to_pints(volume)
        label = '<b>%s</b> (%.1f)' % (username, pints)
        data.append((label, pints))

    other_vol = 0
    for username, pints in data[10:]:
        other_vol += pints

    def _sort_vol_desc(a, b):
        return cmp(b[1], a[1])

    data.sort(_sort_vol_desc)
    data = data[:10]
    data.reverse()

    if other_vol:
        label = '<b>%s</b> (%.1f)' % ('all others', other_vol)
        data.append((label, other_vol))

    res = {
      'series': [
        {
          'type': 'pie',
          'name': 'Drinkers by Volume',
          'data': data,
        }
      ],
      'yAxis': {
        'min': 0,
      },
      'chart': {
        'defaultSeriesType': 'column',
      },
      'tooltip': {
        'enabled': False,
      },
    }
    return res

def _weekday_chart_common(vals):
    labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    # convert from 0=Monday to 0=Sunday
    #vals.insert(0, vals.pop(-1))

    res = {
      'xAxis': {
        'categories': labels,
      },
      'yAxis': {
        'min': 0,
      },
      'series': [
        {'data': vals},
      ],
      'tooltip': {
        'enabled': False,
      },
      'chart': {
        'defaultSeriesType': 'column',
      }
    }
    return res
