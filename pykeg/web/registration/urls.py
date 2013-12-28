from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic.base import TemplateView

from pykeg.web.registration.views import RegistrationView


urlpatterns = patterns('',
                       url(r'^register/$',
                           RegistrationView.as_view(),
                           name='registration_register'),
                       url(r'^register/closed/$',
                           TemplateView.as_view(template_name='registration/registration_closed.html'),
                           name='registration_disallowed'),
                       (r'', include('registration.auth_urls')),
                       )
