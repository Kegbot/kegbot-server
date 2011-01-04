from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.kegadmin.views',
      ### main page
      url(r'^$', 'kegadmin_main', name='kegadmin-main'),
      url(r'^taps/$', 'tap_list', name='kegadmin-tap-list'),
      url(r'^taps/(?P<tap_id>\d+)/$', 'edit_tap', name='kegadmin-edit-tap'),
      url(r'^get-backup/$', 'generate_backup', name='kegadmin-get-backup'),
)

