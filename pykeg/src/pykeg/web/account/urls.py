from django.conf.urls.defaults import *
from pykeg.core import features

urlpatterns = patterns('pykeg.web.account.views',
    url(r'^$', 'account_main', name='kb-account-main'),
    url(r'^mugshot/$', 'edit_mugshot', name='account-mugshot'),
)

if features.use_facebook():
  urlpatterns += patterns('',
      url(r'fb-settings/$', 'pykeg.web.contrib.facebook.views.account_settings', name='fb-account-settings'),
  )
