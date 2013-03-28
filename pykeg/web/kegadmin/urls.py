from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns('pykeg.web.kegadmin.views',
    ### main page
    url(r'^$', 'dashboard', name='kegadmin-dashboard'),
    url(r'^settings/$', 'general_settings', name='kegadmin-main'),

    url(r'^taps/$', 'tap_list', name='kegadmin-taps'),
    url(r'^taps/create/$', 'add_tap', name='kegadmin-add-tap'),
    url(r'^taps/(?P<tap_id>\d+)/$', 'tap_detail', name='kegadmin-edit-tap'),

    url(r'^users/$', 'user_list', name='kegadmin-users'),
    url(r'^users/create/$', 'add_user', name='kegadmin-add-user'),
    url(r'^users/(?P<user_id>\d+)/$', 'user_detail', name='kegadmin-edit-user'),

    url(r'^backup-restore/$', 'backup_restore', name='kegadmin-backup-restore'),
    url(r'^backup-restore/dump/$', 'generate_backup', name='kegadmin-get-backup'),
    url(r'^connections/', include('pykeg.connections.urls')),
    url(r'^edit-connections/$', 'connections', name='kegadmin-connections'),
    url(r'^logs/$', 'logs', name='kegadmin-logs'),
    url(r'^autocomplete/beer/$', 'autocomplete_beer_type',
      name='kegadmin-autocomplete-beer'),
    url(r'^autocomplete/user/$', 'autocomplete_user',
      name='kegadmin-autocomplete-user'),
)

urlpatterns += patterns('pykeg.connections.twitter.views',
    url('^redirect/$', 'site_twitter_redirect', name='site_twitter_redirect'),
    url('^callback/$', 'site_twitter_callback', name='site_twitter_callback'),
)
