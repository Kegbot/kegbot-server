from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.api.views',
    url(r'^last-drink-id/$', 'last_drink_id'),
    url(r'^last-drinks/$', 'last_drinks'),
    url(r'^last-drinks-html/$', 'last_drinks_html'),
    url(r'^all-drinks/$', 'all_drinks'),
    url(r'^all-kegs/$', 'all_kegs'),
    url(r'^all-taps/$', 'all_taps'),
)
