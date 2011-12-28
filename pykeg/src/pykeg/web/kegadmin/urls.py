from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.kegadmin.views',
      ### main page
      url(r'^$', 'kegadmin_main', name='kegadmin-main'),
      url(r'^taps/$', 'tap_list', name='kegadmin-taps'),
      url(r'^taps/(?P<tap_id>\d+)/$', 'edit_tap', name='kegadmin-edit-tap'),
      url(r'^backup-restore/$', 'backup_restore', name='kegadmin-backup-restore'),
      url(r'^backup-restore/dump/$', 'generate_backup', name='kegadmin-get-backup'),

      url(r'^edit-keg/(?P<keg_id>\d+)/$', 'edit_keg', name='kegadmin-edit-keg'),

      url(r'^do-end-keg/$', 'do_end_keg', name='kegadmin-do-end-keg'),
)

