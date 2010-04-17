from django.conf.urls.defaults import *

urlpatterns = patterns('kegweb.contrib.facebook.views',
    url(r'update-perms/$', 'update_perms', name='fb-update-perms'),
    url(r'status-update/$', 'status_update', name='fb-status-update'),
    url(r'settings/$', 'account_settings', name='fb-account-settings'),
)
