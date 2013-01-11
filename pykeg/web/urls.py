# Copyright 2013 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from pykeg.core import features

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_complete
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_done
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

from registration.views import register
from pykeg.web.kegweb.forms import KegbotRegistrationForm

urlpatterns = patterns('',
    ### django admin site
    (r'^admin/', include(admin.site.urls)),

    ### api
    (r'^(?P<kbsite_name>)api/', include('pykeg.web.api.urls')),

    ### kegbot account
    (r'^account/', include('pykeg.web.account.urls')),

    ### auth account
    (r'^accounts/', include('pykeg.web.registration.urls')),
    url(r'^accounts/password/reset/$', password_reset, {'template_name':
     'registration/password_reset.html'}, name="password-reset"),
    (r'^accounts/password/reset/done/$', password_reset_done, {'template_name':
     'registration/password_reset_done.html'}),
    (r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {'template_name':
     'registration/password_reset_confirm.html'}),
    (r'^accounts/password/reset/complete/$', password_reset_complete, {'template_name':
     'registration/password_reset_complete.html'}),

    ### django-registration
    url(r'^(?P<kbsite_name>)accounts/register/$', register,
      {'form_class': KegbotRegistrationForm},
      name='registration_register',
    ),
    (r'^accounts/', include('registration.urls')),

    ### socialregistration
    (r'^sr/', include('socialregistration.urls', namespace='socialregistration')),

    ### setup
    (r'^(?P<kbsite_name>)setup/', include('pykeg.web.setup_wizard.urls')),

    ### charts
    (r'^(?P<kbsite_name>)charts/', include('pykeg.web.charts.urls')),

    ### kegadmin
    (r'^(?P<kbsite_name>)kegadmin/', include('pykeg.web.kegadmin.urls')),
)

if features.use_facebook():
  urlpatterns += patterns('',
      ### facebook kegweb stuff
      (r'^(?P<kbsite_name>)fb/', include('pykeg.web.contrib.facebook.urls')),
  )

if settings.DEBUG:
  urlpatterns += staticfiles_urlpatterns()
  urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
    url(r'^favicon.ico$', 'django.views.generic.simple.redirect_to',
      {'url': '/site_media/images/favicon.ico'}),
  )

### sentry
if settings.HAVE_SENTRY:
  urlpatterns += patterns('',
      (r'^sentry/', include('sentry.web.urls')),
  )

### main kegweb urls
urlpatterns += patterns('',
  (r'^(?P<kbsite_name>)', include('pykeg.web.kegweb.urls')),
)
