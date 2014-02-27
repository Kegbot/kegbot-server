from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns('pykeg.web.kegadmin.views',
    ### main page
    url(r'^$', 'dashboard', name='kegadmin-dashboard'),
    url(r'^settings/$', 'general_settings', name='kegadmin-main'),

    url(r'^beers/$', 'beverages_list', name='kegadmin-beverages'),
    url(r'^beers/add/$', 'beverage_add', name='kegadmin-add-beverage'),
    url(r'^beers/(?P<beer_id>\d+)/$', 'beverage_detail', name='kegadmin-edit-beverage'),

    url(r'^kegs/$', 'keg_list', name='kegadmin-kegs'),
    url(r'^kegs/add/$', 'keg_add', name='kegadmin-add-keg'),
    url(r'^kegs/(?P<keg_id>\d+)/$', 'keg_detail', name='kegadmin-edit-keg'),

    url(r'^brewers/$', 'beverage_producer_list', name='kegadmin-beverage-producers'),
    url(r'^brewers/add/$', 'beverage_producer_add', name='kegadmin-add-beverage-producer'),
    url(r'^brewers/(?P<brewer_id>\d+)/$', 'beverage_producer_detail', name='kegadmin-edit-beverage-producer'),

    url(r'^taps/$', 'tap_list', name='kegadmin-taps'),
    url(r'^taps/create/$', 'add_tap', name='kegadmin-add-tap'),
    url(r'^taps/(?P<tap_id>\d+)/$', 'tap_detail', name='kegadmin-edit-tap'),

    url(r'^users/$', 'user_list', name='kegadmin-users'),
    url(r'^users/create/$', 'add_user', name='kegadmin-add-user'),
    url(r'^users/(?P<user_id>\d+)/$', 'user_detail', name='kegadmin-edit-user'),

    url(r'^drinks/$', 'drink_list', name='kegadmin-drinks'),
    url(r'^drinks/(?P<drink_id>\d+)/$', 'drink_edit', name='kegadmin-edit-drink'),

    url(r'^tokens/$', 'token_list', name='kegadmin-tokens'),
    url(r'^tokens/create/$', 'add_token', name='kegadmin-add-token'),
    url(r'^tokens/(?P<token_id>\d+)/$', 'token_detail', name='kegadmin-edit-token'),

    url(r'^logs/$', 'logs', name='kegadmin-logs'),
    url(r'^autocomplete/beverage/$', 'autocomplete_beverage',
      name='kegadmin-autocomplete-beverage'),
    url(r'^autocomplete/user/$', 'autocomplete_user',
      name='kegadmin-autocomplete-user'),
    url(r'^autocomplete/token/$', 'autocomplete_token',
      name='kegadmin-autocomplete-token'),

    url(r'^plugin/(?P<plugin_name>\w+)/$', 'plugin_settings', name='kegadmin-plugin-settings'),
)

from pykeg.plugin import util
if util.get_plugins():
    urlpatterns += util.get_admin_urls()
