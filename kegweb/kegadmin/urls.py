from django.conf.urls.defaults import *

urlpatterns = patterns('kegweb.kegadmin.views',
      ### main page
      url(r'^$', 'kegadmin_main', name='kegadmin-main'),
)

