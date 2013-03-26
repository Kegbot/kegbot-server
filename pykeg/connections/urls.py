from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns('',
    url('^twitter/', include('pykeg.connections.twitter.urls')),
)

