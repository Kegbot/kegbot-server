from django.conf.urls.defaults import *
from pykeg.core import features

urlpatterns = patterns('pykeg.web.account.views',
    url(r'^$', 'account_main', name='kb-account-main'),
    url(r'^mugshot/$', 'edit_mugshot', name='account-mugshot'),
    url(r'^regenerate-api-key/$', 'regenerate_api_key', name='regen-api-key'),
)

if features.use_facebook():
  urlpatterns += patterns('',
      url(r'fb-settings/$', 'pykeg.web.contrib.facebook.views.account_settings', name='fb-account-settings'),
  )

if features.use_twitter():
  urlpatterns += patterns('',
      url(r'twitter-settings/$', 'pykeg.web.contrib.twitter.views.account_settings', name='twitter-account-settings'),
  )
