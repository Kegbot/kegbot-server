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

urlpatterns = patterns('pykeg.web.api.views',

    url(r'^auth-token/(?P<auth_device>[\w\.]+)\.(?P<token_value>\w+)/?$',
        'get_auth_token'),
    url(r'^drink/?$', 'all_drinks'),
    url(r'^drink/(?P<drink_id>\d+)/?$', 'get_drink'),
    url(r'^session/?$', 'all_sessions'),
    url(r'^session/(?P<session_id>\d+)/?$', 'get_session'),
    url(r'^event/?$', 'all_events'),
    url(r'^event/html/?$', 'recent_events_html'),
    url(r'^sound-event/?$', 'all_sound_events'),
    url(r'^keg/?$', 'all_kegs'),
    url(r'^keg/(?P<keg_id>\d+)/?$', 'get_keg'),
    url(r'^keg/(?P<keg_id>\d+)/drinks/?$', 'get_keg_drinks'),
    url(r'^keg/(?P<keg_id>\d+)/sessions/?$', 'get_keg_sessions'),
    url(r'^tap/?$', 'all_taps'),
    url(r'^tap/(?P<tap_id>[\w\.]+)/?$', 'tap_detail'),
    url(r'^thermo-sensor/?$', 'all_thermo_sensors'),
    url(r'^thermo-sensor/(?P<sensor_name>[^/]+)/?$', 'get_thermo_sensor'),
    url(r'^thermo-sensor/(?P<sensor_name>[^/]+)/logs/?$', 'get_thermo_sensor_logs'),
    url(r'^user/(?P<username>\w+)/?$', 'get_user'),
    url(r'^user/(?P<username>\w+)/drinks/?$', 'get_user_drinks'),
    url(r'^user/(?P<username>\w+)/stats/?$', 'get_user_stats'),

    url(r'^last-drink-id/?$', 'last_drink_id'),
    url(r'^last-drinks/?$', 'last_drinks'),
    url(r'^last-drinks-html/?$', 'last_drinks_html'),

    url(r'^get-access-token/?$', 'get_access_token'),

    url(r'', 'default_handler'),

)
