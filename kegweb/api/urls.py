from django.conf.urls.defaults import *

urlpatterns = patterns('kegweb.api.views',
    url(r'^last-drinks/$', 'last_drinks'),
    url(r'^all-drinks/$', 'all_drinks'),
    url(r'^all-kegs/$', 'all_kegs'),
    url(r'^all-taps/$', 'all_taps'),
)
