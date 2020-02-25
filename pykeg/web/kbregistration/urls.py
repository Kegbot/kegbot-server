from django.conf.urls import include
from django.conf.urls import url

from pykeg.web.kbregistration.forms import PasswordResetForm
from pykeg.web.kbregistration import views
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
)

urlpatterns = [
    url(r'^register/?$',
        views.register,
        name='registration_register'),
    url(r'^password/change/$',
        PasswordChangeView.as_view(),
        name='password_change'),
    url(r'^password/change/done/$',
        PasswordChangeDoneView.as_view(),
        name='password_change_done'),
    url(r'^password/reset/$',
        PasswordResetView.as_view(),
        kwargs={'password_reset_form': PasswordResetForm},
        name='password_reset'),
    url(r'^password/reset/done/$',
        PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    url(r'^password/reset/complete/$',
        PasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    url('', include('django.contrib.auth.urls')),
]
