from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from pykeg.web.kbregistration.forms import PasswordResetForm

urlpatterns = patterns('pykeg.web.kbregistration.views',
    url(r'^register/?$', 'register', name='registration_register'),
)

urlpatterns += patterns('',
                       url(r'^password/change/$',
                           auth_views.password_change,
                           name='password_change'),
                       url(r'^password/change/done/$',
                           auth_views.password_change_done,
                           name='password_change_done'),
                       url(r'^password/reset/$',
                           auth_views.password_reset,
                           kwargs={'password_reset_form': PasswordResetForm},
                           name='password_reset'),
                       url(r'^password/reset/done/$',
                           auth_views.password_reset_done,
                           name='password_reset_done'),
                       url(r'^password/reset/complete/$',
                           auth_views.password_reset_complete,
                           name='password_reset_complete'),
                       url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm,
                           name='password_reset_confirm'),

                       url('', include('registration.auth_urls')))
