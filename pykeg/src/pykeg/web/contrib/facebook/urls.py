from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.contrib.facebook.views',
    url(r'update-perms/$', 'update_perms', name='fb-update-perms'),
    url(r'status-update/$', 'status_update', name='fb-status-update'),
)
