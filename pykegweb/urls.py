import os.path

from django.conf.urls.defaults import *

def basedir():
   """ Get the pwd of this module, eg for use setting absolute paths """
   return os.path.abspath(os.path.dirname(__file__))

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'', include('pykegweb.kegweb.urls')),
)

urlpatterns += patterns('',
      (r'^site_media/(.*)$',
         'django.views.static.serve',
         {'document_root': os.path.join(basedir(), 'media')}),
)
