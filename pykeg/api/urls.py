from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from . import views, views_account

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
    # Must precede the router so it wins over the users/{pk} detail route.
    path("users/me", views.me),
    path("", include(router.urls)),
    path("account/activate", views_account.activate),
    path("account/confirm-email", views_account.confirm_email),
    path("account/email", views_account.change_email),
    path("account/mugshot", views_account.mugshot),
    path("account/password", views_account.change_password),
    path("account/regenerate-api-key", views_account.regenerate_api_key),
    path("auth/api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("auth/login", views.login),
    path("auth/logout", views.logout),
    path("auth/password-reset", views_account.password_reset),
    path("auth/password-reset-confirm", views_account.password_reset_confirm),
    path("auth/register", views_account.register),
    path("status", views.system_status),
    path("schema", SpectacularAPIView.as_view(), name="api-schema"),
    path("docs", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
]
