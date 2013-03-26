from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic import TemplateView

from registration.views import activate
from registration.views import register

urlpatterns = patterns('',
                       url(r'^activate/complete/$',
                           TemplateView.as_view(template_name='registration/activation_complete.html'),
                           name='registration_activation_complete'),
                       url(r'^activate/(?P<activation_key>\w+)/$',
                           activate,
                           {'backend': 'pykeg.web.registration.KegbotRegistrationBackend'},
                           name='registration_activate'),
                       url(r'^register/$',
                           register,
                           {'backend': 'pykeg.web.registration.KegbotRegistrationBackend'},
                           name='registration_register'),
                       url(r'^register/complete/$',
                           TemplateView.as_view(template_name='registration/registration_complete.html'),
                           name='registration_complete'),
                       url(r'^register/closed/$',
                           TemplateView.as_view(template_name='registration/registration_closed.html'),
                           name='registration_disallowed'),
                       (r'', include('registration.auth_urls')),
)
