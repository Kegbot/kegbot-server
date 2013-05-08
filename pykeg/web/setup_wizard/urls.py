from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns('pykeg.web.setup_wizard.views',
  url(r'^$', 'start', name='setup_wizard_start'),
  url(r'^create/$', 'create_or_import', name='setup_create_or_import'),
  url(r'^settings/$', 'site_settings', name='setup_site_settings'),
  url(r'^admin-user/$', 'admin', name='setup_admin'),
  url(r'^finished/$', 'finish', name='setup_finish'),
)
