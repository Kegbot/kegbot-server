# Copyright 2011 Mike Wakerly <opensource@hoho.com>
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

from pykeg.core import models
from pykeg.core import units

def to_pints(volume):
  return float(units.Quantity(volume).InPints())

class ChartError(Exception):
  """Base chart exception."""

def TemperatureSensorChart(sensor):
  """ Shows a simple line plot of a specific temperature sensor.

  Syntax:
    {% chart sensor <sensorname> width height %}
  Args:
    sensorname - the nice_name of a ThermoSensor
  """
  if not isinstance(sensor, models.ThermoSensor):
    raise ChartError('Bad sensor given')

  hours = 6
  now = datetime.datetime.now()
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

def KegVolumeChart(keg):
  if not isinstance(keg, models.Keg):
    raise ChartError('Bad value given for keg')
  stats = keg.GetStats()

  served = units.Quantity(stats.total_volume_ml)
  served_pints = to_pints(served)
  full_pints = to_pints(keg.full_volume())
  remain_pints = full_pints - served_pints

  res = {
    'chart': {
      'defaultSeriesType': 'bar',
    },
    'series': [
      {'data': [served_pints]},
    ],
    'tooltip': {
      'enabled': False,
    },
    'xAxis': {
      'categories': ['Served'],
      'labels': {
        'enabled': False,
      },
      'gridLineWidth': 0,
    },
    'yAxis': {
      'endOnTick': False,
      'min': 0,
      'max': full_pints,
      'lineWidth': 0,
      'labels': {
        'enabled': False,
      },
    },
  }
  return res

def VolumeByWeekday(stats):
  """ Shows a histogram of volume by day of the week.

  Syntax:
    {% chart volume_by_day <stats> width height %}
  Args:
    stats - a stats object containing volume_by_day_of_week
  """
  volmap = [0] * 7
  vols = stats.volume_by_day_of_week
  if not volmap:
    raise ChartError('Daily volumes unavailable')

  for v in vols:
    volmap[int(v.weekday)] += to_pints(v.volume_ml)
  return _DayOfWeekChart(volmap)

def UserSessionsByWeekday(user):
  """Shows a user's total session by volume by day of week."""
  if not isinstance(user, models.User):
    raise ChartError('Bad value for user')
  chunks = user.user_session_chunks.all()
  weekdays = [0] * 7
  for chunk in chunks:
    # Convert from Sunday = 6 to Sunday = 0
    weekday = (chunk.starttime.weekday() + 1) % 7
    weekdays[weekday] += to_pints(chunk.volume_ml)
  return _DayOfWeekChart(weekdays)

def SessionVolumes(sessions):
  buckets = [0]*6
  labels = [
    '<1',
    '1.0-1.9',
    '2.0-2.9',
    '3.0-3.9',
    '4.0-4.9',
    '5+'
  ]
  for sess in sessions:
    pints = round(to_pints(sess.volume_ml), 1)
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

def UsersByVolume(stats):
  vols = stats.volume_by_drinker
  if not vols:
    raise ChartError('no data')

  volmap = {}
  data = []
  for entry in vols:
    pints = to_pints(entry.volume_ml)
    label = '<b>%s</b> (%.1f)' % (entry.username, pints)
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

def UserSessionChunks(user_chunk):
  if not isinstance(user_chunk, models.UserSessionChunk):
    raise ChartUnavailableError, "Must give user chunk as argument"

  max_pints = user_chunk.session.UserChunksByVolume()
  if not max_pints:
    raise ChartUnavailableError, "Error: session corrupt"
  max_pints = to_pints(max_pints[0].volume_ml)
  drinks = user_chunk.GetDrinks()
  totals = {}
  for drink in drinks:
    if drink.keg:
      label = 'keg %i' % drink.keg.seqn
    else:
      label = 'unknown keg'
    totals[label] = totals.get(label, 0) + to_pints(drink.volume_ml)

  series = []
  for name, tot in totals.iteritems():
    series.append({
      'name': name,
      'data': [tot],
    })

  res = {
    'xAxis': {
      'categories': ['Pints'],
    },
    'yAxis': {
      'max': max_pints,
    },
    'series': series,
    'tooltip': {
      'enabled': False,
    },
    'chart': {
      'defaultSeriesType': 'bar',
    },
    'legend': {
      'enabled': True,
    },
    'plotOptions': {
      'series': {
        'stacking': 'normal',
      },
    },
  }
  return res

def _DayOfWeekChart(vals):
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
