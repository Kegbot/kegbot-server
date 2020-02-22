# Copyright 2014 Bevbot LLC, All Rights Reserved
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
from django.conf.urls.static import static
from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = [
    # api
    url(r'^api/(?:v1/)?', include('pykeg.web.api.urls')),

    # kegbot account
    url(r'^account/', include('pykeg.web.account.urls')),

    # auth account
    url(r'^accounts/', include('pykeg.web.kbregistration.urls')),

    # kegadmin
    url(r'^kegadmin/', include('pykeg.web.kegadmin.urls')),

    # Shortcuts
    url(r'^link/?$', RedirectView.as_view(pattern_name='kegadmin-link-device')),
]

if 'pykeg.web.setup_wizard' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^setup/', include('pykeg.web.setup_wizard.urls')),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.KEGBOT_ENABLE_ADMIN:
    urlpatterns += [
        url(r'^admin/', include(admin.site.urls)),
    ]

# main kegweb urls
urlpatterns += [
    url(r'^', include('pykeg.web.kegweb.urls')),
]
