from django.conf import settings
from django.conf.urls.defaults import *

if settings.DEBUG:
  urlpatterns = patterns('pykeg.web.setup_wizard.views',
      url(r'^$', 'start', name='setup_wizard_start'),
      url(r'^settings/$', 'site_settings', name='setup_site_settings'),
      url(r'^admin/$', 'admin', name='setup_admin'),
      url(r'^finish/$', 'finish', name='setup_finish'),
  )
else:
  # For safety, disable setup when not in DEBUG mode.
  urlpatterns = patterns('')
