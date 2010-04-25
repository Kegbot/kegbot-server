from django.conf.urls.defaults import *

urlpatterns = patterns('kegweb.kegadmin.views',
      ### main page
      (r'^$', 'kegadmin_main'),
)

