from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.urls import path

from pykeg.plugin import util
from pykeg.web.account import views

urlpatterns = [
    path("", views.account_main, name="kb-account-main"),
    path(
        "activate/<str:activation_key>/",
        views.activate_account,
        name="activate-account",
    ),
    path("password/done/", PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password/", PasswordChangeView.as_view(), name="password_change"),
    path("profile/", views.edit_profile, name="account-profile"),
    path("invite/", views.invite, name="account-invite"),
    path("confirm-email/<str:token>", views.confirm_email, name="account-confirm-email"),
    path("notifications/", views.notifications, name="account-notifications"),
    path("regenerate-api-key/", views.regenerate_api_key, name="regen-api-key"),
    path("plugin/<str:plugin_name>/", views.plugin_settings, name="account-plugin-settings"),
]

urlpatterns += util.get_account_urls()
