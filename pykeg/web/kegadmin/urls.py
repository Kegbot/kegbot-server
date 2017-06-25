from django.conf import settings
from django.conf.urls import url

from pykeg.plugin import util
from pykeg.web.kegadmin import views

urlpatterns = [
    # main page
    url(r'^$', views.dashboard, name='kegadmin-dashboard'),
    url(r'^settings/general/$', views.general_settings, name='kegadmin-main'),
    url(r'^settings/location/$', views.location_settings, name='kegadmin-location-settings'),
    url(r'^settings/advanced/$', views.advanced_settings, name='kegadmin-advanced-settings'),

    url(r'^bugreport/$', views.bugreport, name='kegadmin-bugreport'),
    url(r'^export/$', views.export, name='kegadmin-export'),

    url(r'^beers/$', views.beverages_list, name='kegadmin-beverages'),
    url(r'^beers/add/$', views.beverage_add, name='kegadmin-add-beverage'),
    url(r'^beers/(?P<beer_id>\d+)/$', views.beverage_detail, name='kegadmin-edit-beverage'),

    url(r'^devices/link/$', views.link_device, name='kegadmin-link-device'),

    url(r'^kegs/$', views.keg_list, name='kegadmin-kegs'),
    url(r'^kegs/online/$', views.keg_list_online, name='kegadmin-kegs-online'),
    url(r'^kegs/available/$', views.keg_list_available, name='kegadmin-kegs-available'),
    url(r'^kegs/kicked/$', views.keg_list_kicked, name='kegadmin-kegs-kicked'),
    url(r'^kegs/add/$', views.keg_add, name='kegadmin-add-keg'),
    url(r'^kegs/(?P<keg_id>\d+)/$', views.keg_detail, name='kegadmin-edit-keg'),

    url(r'^brewers/$', views.beverage_producer_list, name='kegadmin-beverage-producers'),
    url(r'^brewers/add/$', views.beverage_producer_add, name='kegadmin-add-beverage-producer'),
    url(r'^brewers/(?P<brewer_id>\d+)/$',
        views.beverage_producer_detail,
        name='kegadmin-edit-beverage-producer'),

    url(r'^controllers/$', views.controller_list, name='kegadmin-controllers'),
    url(r'^controllers/(?P<controller_id>\d+)/$',
        views.controller_detail, name='kegadmin-edit-controller'),

    url(r'^taps/$', views.tap_list, name='kegadmin-taps'),
    url(r'^taps/create/$', views.add_tap, name='kegadmin-add-tap'),
    url(r'^taps/(?P<tap_id>\d+)/$', views.tap_detail, name='kegadmin-edit-tap'),

    url(r'^users/$', views.user_list, name='kegadmin-users'),
    url(r'^users/(?P<user_id>\d+)/$', views.user_detail, name='kegadmin-edit-user'),

    url(r'^drinks/$', views.drink_list, name='kegadmin-drinks'),
    url(r'^drinks/(?P<drink_id>\d+)/$', views.drink_edit, name='kegadmin-edit-drink'),

    url(r'^tokens/$', views.token_list, name='kegadmin-tokens'),
    url(r'^tokens/create/$', views.add_token, name='kegadmin-add-token'),
    url(r'^tokens/(?P<token_id>\d+)/$', views.token_detail, name='kegadmin-edit-token'),

    url(r'^autocomplete/beverage/$', views.autocomplete_beverage,
        name='kegadmin-autocomplete-beverage'),
    url(r'^autocomplete/user/$', views.autocomplete_user,
        name='kegadmin-autocomplete-user'),
    url(r'^autocomplete/token/$', views.autocomplete_token,
        name='kegadmin-autocomplete-token'),

    url(r'^plugin/(?P<plugin_name>\w+)/$', views.plugin_settings, name='kegadmin-plugin-settings'),
]

if not settings.EMBEDDED:
    urlpatterns += [
        url(r'^email/$', views.email, name='kegadmin-email'),
        url(r'^logs/$', views.logs, name='kegadmin-logs'),
        url(r'^users/create/$', views.add_user, name='kegadmin-add-user'),
        url(r'^workers/$', views.workers, name='kegadmin-workers'),
    ]

if util.get_plugins():
    urlpatterns += util.get_admin_urls()
