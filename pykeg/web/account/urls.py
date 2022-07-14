from django.conf.urls import url
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView

from pykeg.plugin import util
from pykeg.web.account import views

urlpatterns = [
    url(r"^$", views.account_main, name="kb-account-main"),
    url(
        r"^activate/(?P<activation_key>[0-9a-zA-Z]+)/$",
        views.activate_account,
        name="activate-account",
    ),
    url(r"^password/done/$", PasswordChangeDoneView.as_view(), name="password_change_done"),
    url(r"^password/$", PasswordChangeView.as_view(), name="password_change"),
    url(r"^profile/$", views.edit_profile, name="account-profile"),
    url(r"^invite/$", views.invite, name="account-invite"),
    url(r"^confirm-email/(?P<token>.+)$", views.confirm_email, name="account-confirm-email"),
    url(r"^notifications/$", views.notifications, name="account-notifications"),
    url(r"^regenerate-api-key/$", views.regenerate_api_key, name="regen-api-key"),
    url(r"^plugin/(?P<plugin_name>\w+)/$", views.plugin_settings, name="account-plugin-settings"),
]

urlpatterns += util.get_account_urls()
