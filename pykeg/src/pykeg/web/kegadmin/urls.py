from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.kegadmin.views',
      ### main page
      url(r'^$', 'kegadmin_main', name='kegadmin-main'),
      url(r'^change-kegs/$', 'change_kegs', name='kegadmin-change-kegs'),
      url(r'^edit-taps/$', 'edit_taps', name='kegadmin-edit-taps'),
)

