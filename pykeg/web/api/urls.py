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

from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns('pykeg.web.api.views',

    ### General endpoints

    url(r'^status/?$', 'get_status'),
    url(r'^version/?$', 'get_version'),

    ### API authorization

    url(r'^login/?$', 'login'),
    url(r'^logout/?$', 'logout'),
    url(r'^get-api-key/?$', 'get_api_key'),

    url(r'^devices/link/?$', 'link_device_new'),
    url(r'^devices/link/status/(?P<code>[^/]+)?$', 'link_device_status'),

    ### Kegbot objects

    url(r'^auth-tokens/(?P<auth_device>[\w\.]+)/(?P<token_value>\w+)/?$',
        'get_auth_token'),
    url(r'^auth-tokens/(?P<auth_device>[\w\.]+)/(?P<token_value>\w+)/assign/?$',
        'assign_auth_token'),

    url(r'^controllers/?$', 'all_controllers'),
    url(r'^controllers/(?P<controller_id>\d+)/?$', 'get_controller'),

    url(r'^drinks/?$', 'all_drinks'),
    url(r'^drinks/(?P<drink_id>\d+)/?$', 'get_drink'),
    url(r'^drinks/(?P<drink_id>\d+)/add-photo/?$', 'add_drink_photo'),
    url(r'^cancel-drink/?$', 'cancel_drink'),

    url(r'^events/?$', 'all_events'),

    url(r'^flow-meters/?$', 'all_flow_meters'),
    url(r'^flow-meters/(?P<flow_meter_id>\d+)/?$', 'get_flow_meter'),

    url(r'^flow-toggles/?$', 'all_flow_toggles'),
    url(r'^flow-toggles/(?P<flow_toggle_id>\d+)/?$', 'get_flow_toggle'),

    url(r'^kegs/?$', 'all_kegs'),
    url(r'^kegs/(?P<keg_id>\d+)/?$', 'get_keg'),
    url(r'^kegs/(?P<keg_id>\d+)/end/?$', 'end_keg'),
    url(r'^kegs/(?P<keg_id>\d+)/drinks/?$', 'get_keg_drinks'),
    url(r'^kegs/(?P<keg_id>\d+)/events/?$', 'get_keg_events'),
    url(r'^kegs/(?P<keg_id>\d+)/sessions/?$', 'get_keg_sessions'),
    url(r'^kegs/(?P<keg_id>\d+)/stats/?$', 'get_keg_stats'),
    url(r'^keg-sizes/?$', 'get_keg_sizes'),

    url(r'^pictures/?$', 'pictures'),

    url(r'^sessions/?$', 'all_sessions'),
    url(r'^sessions/current/?$', 'current_session'),
    url(r'^sessions/(?P<session_id>\d+)/?$', 'get_session'),
    url(r'^sessions/(?P<session_id>\d+)/stats/?$', 'get_session_stats'),

    url(r'^taps/?$', 'all_taps'),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/activate/?$', 'tap_activate'),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/calibrate/?$', 'tap_calibrate'),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/spill/?$', 'tap_spill'),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/connect-meter/?$', 'tap_connect_meter'),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/disconnect-meter/?$', 'tap_disconnect_meter'),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/connect-toggle/?$', 'tap_connect_toggle'),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/disconnect-toggle/?$', 'tap_disconnect_toggle'),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/?$', 'tap_detail'),

    url(r'^thermo-sensors/?$', 'all_thermo_sensors'),
    url(r'^thermo-sensors/(?P<sensor_name>[^/]+)/?$', 'get_thermo_sensor'),
    url(r'^thermo-sensors/(?P<sensor_name>[^/]+)/logs/?$', 'get_thermo_sensor_logs'),

    url(r'^users/?$', 'user_list'),
    url(r'^users/(?P<username>[\w@.+-_]+)/drinks/?$', 'get_user_drinks'),
    url(r'^users/(?P<username>[\w@.+-_]+)/events/?$', 'get_user_events'),
    url(r'^users/(?P<username>[\w@.+-_]+)/stats/?$', 'get_user_stats'),
    url(r'^users/(?P<username>[\w@.+-_]+)/photo/?$', 'user_photo'),
    url(r'^users/(?P<username>[\w@.+-_]+)/?$', 'get_user'),
    url(r'^new-user/?$', 'register'),

    url(r'^stats/?$', 'get_system_stats'),

    ### Deprecated endpoints

    url(r'^sound-events/?$', 'all_sound_events'),

    ### Catch-all
    url(r'', 'default_handler'),

)
