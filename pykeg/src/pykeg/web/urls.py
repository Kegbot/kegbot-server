import os.path

from pykeg.core import features

from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

def basedir():
  """ Get the pwd of this module, eg for use setting absolute paths """
  return os.path.abspath(os.path.dirname(__file__))

urlpatterns = patterns('',
    ### django admin site
    (r'^admin/(.*)', admin.site.root),

    ### static media
    url(r'^site_media/(.*)$',
      'django.views.static.serve',
      {'document_root': os.path.join(basedir(), 'media')},
      name='site-media'),

    url(r'^media/(.*)$',
     'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True},
     name='media'),

    ### RESTful api
    (r'^api/', include('pykeg.web.api.urls')),

    ### kegadmin
    (r'^kegadmin/', include('pykeg.web.kegadmin.urls')),

    ### main kegweb urls
    (r'', include('pykeg.web.kegweb.urls')),
)

if features.use_facebook():
  urlpatterns += patterns('',
      ### socialregistration
      (r'^sr/', include('socialregistration.urls')),

      ### facebook kegweb stuff
      (r'^fb/', include('pykeg.web.contrib.facebook.urls')),
  )

