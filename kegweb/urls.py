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
    (r'^site_media/(.*)$',
     'django.views.static.serve',
     {'document_root': os.path.join(basedir(), 'media')}),

    (r'^media/(.*)$',
     'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

    ### RESTful api
    (r'^api/beergoggle/', include('kegweb.contrib.beergoggle.urls')),
    (r'^api/', include('kegweb.api.urls')),

    ### kegadmin
    (r'^kegadmin/', include('kegweb.kegadmin.urls')),

    ### main kegweb urls
    (r'', include('kegweb.kegweb.urls')),
)

if features.use_facebook():
  urlpatterns += patterns('',
      ### socialregistration
      (r'^sr/', include('socialregistration.urls')),

      ### facebook kegweb stuff
      (r'^fb/', include('kegweb.contrib.facebook.urls')),
  )

