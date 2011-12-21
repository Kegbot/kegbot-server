# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

"""Chart AJAX views."""

from django.shortcuts import get_object_or_404

from pykeg.core import models
from pykeg.web.api.views import py_to_json
from pykeg.web.charts import charts

@py_to_json
def temperature_sensor_history(request, nice_name):
  sensor = get_object_or_404(models.ThermoSensor, nice_name=nice_name,
      site=request.kbsite)
  return charts.TemperatureSensorChart(sensor)

@py_to_json
def keg_volume(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  return charts.KegVolumeChart(keg)

@py_to_json
def keg_usage_weekdays(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  return charts.KegUsageByWeekday(keg)

@py_to_json
def keg_users_by_volume(request, keg_id):
  keg = get_object_or_404(models.Keg, seqn=keg_id, site=request.kbsite)
  return charts.UsersByVolume(keg)

@py_to_json
def user_usage_weekdays(request, username):
  user = get_object_or_404(models.User, username=username)
  return charts.UserSessionsByWeekday(user)

@py_to_json
def user_usage_sessions(request, username):
  user = get_object_or_404(models.User, username=username)
  sessions = user.user_session_chunks.all()
  return charts.SessionVolumes(sessions)

@py_to_json
def user_session_chunks(request, chunk_id):
  chunk = get_object_or_404(models.UserSessionChunk, site=request.kbsite,
      seqn=chunk_id)
  return charts.UserSessionChunks(chunk)

@py_to_json
def session_users_by_volume(request, session_id):
  session = get_object_or_404(models.DrinkingSession,
      site=request.kbsite, seqn=session_id)
  sessions = user.user_session_chunks.all()
  return charts.SessionVolumes(sessions)

