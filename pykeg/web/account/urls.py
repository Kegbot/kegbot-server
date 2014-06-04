from django.conf.urls import patterns
from django.conf.urls import url

from pykeg.web.account.views import password_change
from pykeg.web.account.views import password_change_done


urlpatterns = patterns('pykeg.web.account.views',
    url(r'^$', 'account_main', name='kb-account-main'),
    url(r'^activate/(?P<activation_key>[0-9a-zA-Z]+)/$', 'activate_account', name='activate-account'),
    url(r'^password/done/$', password_change_done, name='password_change_done'),
    url(r'^password/$', password_change, name='password_change'),
    url(r'^profile/$', 'edit_profile', name='account-profile'),
    url(r'^invite/$', 'invite', name='account-invite'),
    url(r'^notifications/$', 'notifications', name='account-notifications'),
    url(r'^regenerate-api-key/$', 'regenerate_api_key', name='regen-api-key'),
    url(r'^plugin/(?P<plugin_name>\w+)/$', 'plugin_settings', name='account-plugin-settings'),
)

from pykeg.plugin import util
urlpatterns += util.get_account_urls()
