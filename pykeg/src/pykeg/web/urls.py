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

try:
  from registration.views import register
  from pykeg.web.kegweb.forms import KegbotRegistrationForm
  USE_DJANGO_REGISTRATION = True
except ImportError:
  USE_DJANGO_REGISTRATION = False

def basedir():
  """ Get the pwd of this module, eg for use setting absolute paths """
  return os.path.abspath(os.path.dirname(__file__))

urlpatterns = patterns('',
    ### django admin site
    (r'^admin/', include(admin.site.urls)),

    ### static media
    url(r'^media/(.*)$',
     'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT, 'show_indexes': False},
     name='media'),

    (r'^favicon.ico$', 'django.views.generic.simple.redirect_to',
      {'url': '/site_media/images/favicon.ico'}),

    ### RESTful api
    (r'^(?P<kbsite_name>)api/', include('pykeg.web.api.urls')),

    ### account
    (r'^(?P<kbsite_name>)account/', include('pykeg.web.account.urls')),
    (r'^(?P<kbsite_name>)accounts/password/reset/$', password_reset, {'template_name':
     'registration/password_reset.html'}),
    (r'^(?P<kbsite_name>)accounts/password/reset/done/$', password_reset_done, {'template_name':
     'registration/password_reset_done.html'}),
    (r'^(?P<kbsite_name>)accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {'template_name':
     'registration/password_reset_confirm.html'}),
    (r'^(?P<kbsite_name>)accounts/password/reset/complete/$', password_reset_complete, {'template_name':
     'registration/password_reset_complete.html'}),

    ### socialregistration
    (r'^sr/', include('socialregistration.urls')),

    ### charts
    (r'^(?P<kbsite_name>)charts/', include('pykeg.web.charts.urls')),

    ### kegadmin
    (r'^(?P<kbsite_name>)kegadmin/', include('pykeg.web.kegadmin.urls')),

    ### sentry
    (r'^sentry/', include('sentry.web.urls')),

    ### main kegweb urls
    (r'^(?P<kbsite_name>)', include('pykeg.web.kegweb.urls')),
)

if features.use_facebook():
  urlpatterns += patterns('',
      ### facebook kegweb stuff
      (r'^(?P<kbsite_name>)fb/', include('pykeg.web.contrib.facebook.urls')),
  )

### accounts and registration
# uses the stock django-registration views, except we need to override the
# registration class for acocunt/register
if USE_DJANGO_REGISTRATION:
  from django.contrib.auth import views as auth_views
  urlpatterns += patterns('',
    url(r'^(?P<kbsite_name>)accounts/register/$', register,
      {'form_class':KegbotRegistrationForm},
      name='registration_register',
    ),
   (r'^accounts/', include('registration.urls')),
  )

