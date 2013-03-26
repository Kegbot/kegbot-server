from django.conf.urls import patterns
from django.conf.urls import url

from pykeg.core import features
from pykeg.web.account.views import password_change
from pykeg.web.account.views import password_change_done
from pykeg.web.account.views import remove_untappd


urlpatterns = patterns('pykeg.web.account.views',
    url(r'^$', 'account_main', name='kb-account-main'),
    url(r'^connections/$', 'connections', name='account-connections'),
    url(r'^password/done/$', password_change_done, name='password_change_done'),
    url(r'^password/$', password_change, name='password_change'),
    url(r'^mugshot/$', 'edit_mugshot', name='account-mugshot'),
    url(r'^regenerate-api-key/$', 'regenerate_api_key', name='regen-api-key'),
    url(r'^update-foursquare-settings/$', 'update_foursquare_settings', name='update-foursquare-settings'),
    url(r'^remove-foursquare/$', 'remove_foursquare', name='remove-foursquare'),
    url(r'^update-twitter-settings/$', 'update_twitter_settings', name='update-twitter-settings'),
    url(r'^remove-twitter/$', 'remove_twitter', name='remove-twitter'),
)

if features.use_facebook():
  urlpatterns += patterns('',
      url(r'fb-settings/$', 'pykeg.web.contrib.facebook.views.account_settings', name='fb-account-settings'),
  )

if features.use_untappd():
  urlpatterns += patterns('',
      url(r'^remove-untappd/$', remove_untappd, name='remove-untappd'),
  )
