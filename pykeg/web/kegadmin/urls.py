from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.kegadmin.views',
    ### main page
    url(r'^$', 'kegadmin_main', name='kegadmin-main'),
    url(r'^taps/$', 'tap_list', name='kegadmin-taps'),
    url(r'^taps/(?P<tap_id>\d+)/$', 'tap_detail', name='kegadmin-edit-tap'),
    url(r'^backup-restore/$', 'backup_restore', name='kegadmin-backup-restore'),
    url(r'^backup-restore/dump/$', 'generate_backup', name='kegadmin-get-backup'),
    url(r'^connections/', include('pykeg.connections.urls')),
    url(r'^edit-connections/$', 'connections', name='kegadmin-connections'),
    url(r'^logs/$', 'logs', name='kegadmin-logs'),
    url(r'^autocomplete/beer/$', 'autocomplete_beer_type',
      name='kegadmin-autocomplete-beer'),
)

urlpatterns += patterns('pykeg.connections.twitter.views',
    url('^redirect/$', 'site_twitter_redirect', name='site_twitter_redirect'),
    url('^callback/$', 'site_twitter_callback', name='site_twitter_callback'),
)
