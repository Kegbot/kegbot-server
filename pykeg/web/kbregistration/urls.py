from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import include, path

from pykeg.web.kbregistration import views
from pykeg.web.kbregistration.forms import PasswordResetForm

urlpatterns = [
    path("register/", views.register, name="registration_register"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("password/change/done/", PasswordChangeDoneView.as_view(), name="password_change_done"),
    path(
        "password/reset/",
        PasswordResetView.as_view(),
        kwargs={"password_reset_form": PasswordResetForm},
        name="password_reset",
    ),
    path("password/reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "password/reset/complete/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "password/reset/confirm/<str:uidb64>-<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("", include("django.contrib.auth.urls")),
]
