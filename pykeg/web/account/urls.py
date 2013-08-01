from django.conf.urls import patterns
from django.conf.urls import url

from pykeg.core import features
from pykeg.web.account.views import password_change
from pykeg.web.account.views import password_change_done


urlpatterns = patterns('pykeg.web.account.views',
    url(r'^$', 'account_main', name='kb-account-main'),
    url(r'^password/done/$', password_change_done, name='password_change_done'),
    url(r'^password/$', password_change, name='password_change'),
    url(r'^mugshot/$', 'edit_mugshot', name='account-mugshot'),
    url(r'^regenerate-api-key/$', 'regenerate_api_key', name='regen-api-key'),
    url(r'^plugin/(?P<plugin_name>\w+)/$', 'plugin_settings', name='account-plugin-settings'),
)

if features.use_facebook():
    urlpatterns += patterns('',
        url(r'fb-settings/$', 'pykeg.web.contrib.facebook.views.account_settings', name='fb-account-settings'),
    )

from pykeg.plugin import util
urlpatterns += util.get_account_urls()
