from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register("api-keys", views.ApiKeyViewSet)
router.register("auth-tokens", views.AuthenticationTokenViewSet)
router.register("beverage-producers", views.BeverageProducerViewSet)
router.register("beverages", views.BeverageViewSet)
router.register("controllers", views.ControllerViewSet)
router.register("devices", views.DeviceViewSet)
router.register("drinks", views.DrinkViewSet)
router.register("events", views.SystemEventViewSet)
router.register("flow-meters", views.FlowMeterViewSet)
router.register("flow-toggles", views.FlowToggleViewSet)
router.register("invitations", views.InvitationViewSet)
router.register("kegs", views.KegViewSet)
router.register("notification-settings", views.NotificationSettingsViewSet)
router.register("plugin-data", views.PluginDataViewSet)
router.register("sessions", views.DrinkingSessionViewSet)
router.register("stats", views.StatsViewSet)
router.register("taps", views.KegTapViewSet)
router.register("thermo-logs", views.ThermologViewSet)
router.register("thermo-sensors", views.ThermoSensorViewSet)
router.register("users", views.UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("auth/current-user", views.current_user),
    path("auth/login", views.login),
    path("auth/logout", views.logout),
    path("status", views.system_status),
]
