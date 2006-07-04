from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^pykegweb/', include('pykegweb.apps.foo.urls.foo')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'', include('pykegweb.kegweb.urls')),
)
