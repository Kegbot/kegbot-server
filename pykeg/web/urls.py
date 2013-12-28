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

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_complete
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_done
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    ### api
    (r'^api/', include('pykeg.web.api.urls')),

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

    ### socialregistration
    (r'^sr/', include('socialregistration.urls', namespace='socialregistration')),

    ### setup
    (r'^setup/', include('pykeg.web.setup_wizard.urls')),

    ### kegadmin
    (r'^kegadmin/', include('pykeg.web.kegadmin.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
      url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
    )

if settings.KEGBOT_ENABLE_ADMIN:
    urlpatterns += patterns('',
      (r'^admin/', include(admin.site.urls)),
    )

### main kegweb urls
urlpatterns += patterns('',
  (r'^', include('pykeg.web.kegweb.urls')),
)
