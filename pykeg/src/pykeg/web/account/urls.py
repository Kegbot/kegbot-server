from django.conf.urls.defaults import *
from pykeg.core import features

urlpatterns = patterns('pykeg.web.account.views',
    url(r'^$', 'account_main', name='kb-account-main'),
    url(r'^connection/$', 'connections', name='account-connections'),
    url(r'^mugshot/$', 'edit_mugshot', name='account-mugshot'),
    url(r'^regenerate-api-key/$', 'regenerate_api_key', name='regen-api-key'),
    url(r'^update-twitter-settings/$', 'update_twitter_settings', name='update-twitter-settings'),
    url(r'^remove-twitter/$', 'remove_twitter', name='remove-twitter'),
)

if features.use_facebook():
  urlpatterns += patterns('',
      url(r'fb-settings/$', 'pykeg.web.contrib.facebook.views.account_settings', name='fb-account-settings'),
  )
