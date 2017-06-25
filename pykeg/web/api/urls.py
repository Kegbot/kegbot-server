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

from django.conf.urls import url

from . import views

urlpatterns = [
    # General endpoints

    url(r'^status/?$', views.get_status),
    url(r'^version/?$', views.get_version),

    # API authorization

    url(r'^login/?$', views.login),
    url(r'^logout/?$', views.logout),
    url(r'^get-api-key/?$', views.get_api_key),

    url(r'^devices/link/?$', views.link_device_new),
    url(r'^devices/link/status/(?P<code>[^/]+)?$', views.link_device_status),

    # Kegbot objects

    url(r'^auth-tokens/(?P<auth_device>[\w\.]+)/(?P<token_value>\w+)/?$',
        views.get_auth_token),
    url(r'^auth-tokens/(?P<auth_device>[\w\.]+)/(?P<token_value>\w+)/assign/?$',
        views.assign_auth_token),

    url(r'^controllers/?$', views.all_controllers),
    url(r'^controllers/(?P<controller_id>\d+)/?$', views.get_controller),

    url(r'^drinks/?$', views.all_drinks),
    url(r'^drinks/last/?$', views.last_drink),
    url(r'^drinks/(?P<drink_id>\d+)/?$', views.get_drink),
    url(r'^drinks/(?P<drink_id>\d+)/add-photo/?$', views.add_drink_photo),
    url(r'^cancel-drink/?$', views.cancel_drink),

    url(r'^events/?$', views.all_events),

    url(r'^flow-meters/?$', views.all_flow_meters),
    url(r'^flow-meters/(?P<flow_meter_id>\d+)/?$', views.get_flow_meter),

    url(r'^flow-toggles/?$', views.all_flow_toggles),
    url(r'^flow-toggles/(?P<flow_toggle_id>\d+)/?$', views.get_flow_toggle),

    url(r'^kegs/?$', views.all_kegs),
    url(r'^kegs/(?P<keg_id>\d+)/?$', views.get_keg),
    url(r'^kegs/(?P<keg_id>\d+)/end/?$', views.end_keg),
    url(r'^kegs/(?P<keg_id>\d+)/drinks/?$', views.get_keg_drinks),
    url(r'^kegs/(?P<keg_id>\d+)/events/?$', views.get_keg_events),
    url(r'^kegs/(?P<keg_id>\d+)/sessions/?$', views.get_keg_sessions),
    url(r'^kegs/(?P<keg_id>\d+)/stats/?$', views.get_keg_stats),
    url(r'^keg-sizes/?$', views.get_keg_sizes),

    url(r'^pictures/?$', views.pictures),

    url(r'^sessions/?$', views.all_sessions),
    url(r'^sessions/current/?$', views.current_session),
    url(r'^sessions/(?P<session_id>\d+)/?$', views.get_session),
    url(r'^sessions/(?P<session_id>\d+)/stats/?$', views.get_session_stats),

    url(r'^taps/?$', views.all_taps),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/activate/?$', views.tap_activate),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/calibrate/?$', views.tap_calibrate),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/spill/?$', views.tap_spill),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/connect-meter/?$', views.tap_connect_meter),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/disconnect-meter/?$', views.tap_disconnect_meter),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/connect-toggle/?$', views.tap_connect_toggle),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/disconnect-toggle/?$', views.tap_disconnect_toggle),
    url(r'^taps/(?P<meter_name_or_id>[\w\.-]+)/?$', views.tap_detail),

    url(r'^thermo-sensors/?$', views.all_thermo_sensors),
    url(r'^thermo-sensors/(?P<sensor_name>[^/]+)/?$', views.get_thermo_sensor),
    url(r'^thermo-sensors/(?P<sensor_name>[^/]+)/logs/?$', views.get_thermo_sensor_logs),

    url(r'^users/?$', views.user_list),
    url(r'^users/(?P<username>[\w@.+-_]+)/drinks/?$', views.get_user_drinks),
    url(r'^users/(?P<username>[\w@.+-_]+)/events/?$', views.get_user_events),
    url(r'^users/(?P<username>[\w@.+-_]+)/stats/?$', views.get_user_stats),
    url(r'^users/(?P<username>[\w@.+-_]+)/photo/?$', views.user_photo),
    url(r'^users/(?P<username>[\w@.+-_]+)/?$', views.get_user),
    url(r'^new-user/?$', views.register),

    url(r'^stats/?$', views.get_system_stats),

    # Deprecated endpoints

    url(r'^sound-events/?$', views.all_sound_events),

    # Catch-all
    url(r'', views.default_handler),
]
