from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url('^twitter/', include('pykeg.connections.twitter.urls')),
)

