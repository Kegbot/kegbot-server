from django.conf.urls import include, url
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)

from pykeg.web.kbregistration import views
from pykeg.web.kbregistration.forms import PasswordResetForm

urlpatterns = [
    url(r"^register/?$", views.register, name="registration_register"),
    url(r"^password/change/$", PasswordChangeView.as_view(), name="password_change"),
    url(r"^password/change/done/$", PasswordChangeDoneView.as_view(), name="password_change_done"),
    url(
        r"^password/reset/$",
        PasswordResetView.as_view(),
        kwargs={"password_reset_form": PasswordResetForm},
        name="password_reset",
    ),
    url(r"^password/reset/done/$", PasswordResetDoneView.as_view(), name="password_reset_done"),
    url(
        r"^password/reset/complete/$",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    url(
        r"^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    url("", include("django.contrib.auth.urls")),
]
