from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns('pykeg.web.kegadmin.views',
    ### main page
    url(r'^$', 'dashboard', name='kegadmin-dashboard'),
    url(r'^settings/$', 'general_settings', name='kegadmin-main'),

    url(r'^beers/$', 'beer_type_list', name='kegadmin-beer-types'),
    url(r'^beers/(?P<beer_id>\d+)/$', 'beer_type_detail', name='kegadmin-edit-beer-type'),

    url(r'^beer-styles/$', 'beer_style_list', name='kegadmin-beer-styles'),
    url(r'^beer-styles/(?P<style_id>\d+)/$', 'beer_style_detail', name='kegadmin-edit-beer-style'),

    url(r'^brewers/$', 'brewer_list', name='kegadmin-brewers'),
    url(r'^brewers/(?P<brewer_id>\d+)/$', 'brewer_detail', name='kegadmin-edit-brewer'),

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
    url(r'^autocomplete/beer/$', 'autocomplete_beer_type',
      name='kegadmin-autocomplete-beer'),
    url(r'^autocomplete/user/$', 'autocomplete_user',
      name='kegadmin-autocomplete-user'),
    url(r'^autocomplete/token/$', 'autocomplete_token',
      name='kegadmin-autocomplete-token'),

    url(r'^plugin/(?P<plugin_name>\w+)/$', 'plugin_settings', name='kegadmin-plugin-settings'),
)

from pykeg.plugin import util
if util.get_plugins():
    urlpatterns += util.get_admin_urls()
