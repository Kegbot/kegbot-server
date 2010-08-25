from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.api.views',

    url(r'^auth-token/(?P<auth_device>\w+)\.(?P<token_value>\w+)$',
        'get_auth_token'),
    url(r'^drink/$', 'all_drinks'),
    url(r'^keg/$', 'all_kegs'),
    url(r'^tap/$', 'all_taps'),
    url(r'^tap/(?P<tap_id>[\w\.]+)/$', 'tap_detail'),
    url(r'^thermo-sensor/(?P<raw_name>\w+)$', 'get_thermo_sensor'),
    url(r'^thermo-sensor/(?P<raw_name>\w+)/logs$', 'get_thermo_sensor_logs'),
    url(r'^user/(?P<username>\w+)$', 'get_user'),

    url(r'^last-drink-id/$', 'last_drink_id'),
    url(r'^last-drinks/$', 'last_drinks'),
    url(r'^last-drinks-html/$', 'last_drinks_html'),

)
