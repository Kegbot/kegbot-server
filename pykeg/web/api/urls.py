from django.urls import path, re_path

from . import views

# The legacy v1 API is deprecated. Only the endpoints used by
# kegbot-pycore (plus the events feed used by the fullscreen page)
# remain; everything else responds 410 Gone.
urlpatterns = [
    path("status", views.get_status),
    path("auth-tokens/<str:auth_device>/<str:token_value>", views.get_auth_token),
    path("cancel-drink", views.cancel_drink),
    path("controllers", views.all_controllers),
    path("events", views.all_events),
    path("flow-meters", views.all_flow_meters),
    path("taps", views.all_taps),
    path("taps/<str:meter_name_or_id>", views.tap_detail),
    path("thermo-sensors/<str:sensor_name>", views.get_thermo_sensor),
    # Catch-all for retired endpoints.
    re_path(r"", views.gone),
]
