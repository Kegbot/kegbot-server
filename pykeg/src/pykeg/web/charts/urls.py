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

from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.charts.views',
    url(r'^temperature-sensor/(?P<nice_name>\w+)/history/?$',
        'temperature_sensor_history'),
    url(r'^keg/(?P<keg_id>\d+)/volume/?$', 'keg_volume'),
    url(r'^keg/(?P<keg_id>\d+)/usage-by-weekday/?$', 'keg_usage_weekdays'),
    url(r'^keg/(?P<keg_id>\d+)/users-by-volume/?$', 'keg_users_by_volume'),
    url(r'^user/(?P<username>[\w@.+-_]+)/usage-by-weekday/?$', 'user_usage_weekdays'),
    url(r'^user/(?P<username>[\w@.+-_]+)/usage-by-session/?$', 'user_usage_sessions'),
    url(r'^session/(?P<session_id>\d+)/users-by-volume/?$',
        'session_users_by_volume'),
)
