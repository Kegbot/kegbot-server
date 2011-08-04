import os.path

from pykeg.core import features

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_done
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_complete
from django.contrib import admin
admin.autodiscover()

def basedir():
  """ Get the pwd of this module, eg for use setting absolute paths """
  return os.path.abspath(os.path.dirname(__file__))

urlpatterns = patterns('',
    ### django admin site
    (r'^admin/', include(admin.site.urls)),

    ### static media
    url(r'^site_media/(.*)$',
      'django.views.static.serve',
      {'document_root': os.path.join(basedir(), 'media')},
      name='site-media'),

    url(r'^media/(.*)$',
     'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True},
     name='media'),

    (r'^favicon.ico$', 'django.views.generic.simple.redirect_to',
      {'url': '/site_media/images/favicon.ico'}),

    ### RESTful api
    (r'^api/', include('pykeg.web.api.urls')),

    ### account
    (r'^account/', include('pykeg.web.account.urls')),
    (r'^accounts/password/reset/$', password_reset, {'template_name':
     'registration/password_reset.html'}),
    (r'^accounts/password/reset/done/$', password_reset_done, {'template_name':
     'registration/password_reset_done.html'}),
    (r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {'template_name':
     'registration/password_reset_confirm.html'}),
    (r'^accounts/password/reset/complete/$', password_reset_complete, {'template_name':
     'registration/password_reset_complete.html'}),

    ### socialregistration
    (r'^sr/', include('socialregistration.urls')),

    ### charts
    (r'^(?P<kbsite_name>)charts/', include('pykeg.web.charts.urls')),

    ### kegadmin
    (r'^(?P<kbsite_name>)kegadmin/', include('pykeg.web.kegadmin.urls')),

    ### main kegweb urls
    (r'(?P<kbsite_name>)', include('pykeg.web.kegweb.urls')),
)

if features.use_facebook():
  urlpatterns += patterns('',
      ### facebook kegweb stuff
      (r'^fb/', include('pykeg.web.contrib.facebook.urls')),
  )

if features.use_twitter():
  urlpatterns += patterns('',
      ### twitter kegweb stuff
      (r'^twitter/', include('pykeg.web.contrib.twitter.urls')),
  )

