# Copyright 2014 Kegbot Project contributors
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
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic.base import RedirectView

from pykeg.web.account import urls as account_urls
from pykeg.web.api import urls as api_urls
from pykeg.web.kbregistration import urls as kbregistration_urls
from pykeg.web.kegadmin import urls as kegadmin_urls
from pykeg.web.kegweb import urls as kegweb_urls
from pykeg.web.setup_wizard import urls as setup_wizard_urls

urlpatterns = [
    re_path(r"^api/(?:v1/)?", include(api_urls)),
    path("account/", include(account_urls)),
    path("accounts/", include(kbregistration_urls)),
    path("kegadmin/", include(kegadmin_urls)),
    # Shortcuts
    url(r"^link/?$", RedirectView.as_view(pattern_name="kegadmin-link-device")),
]

if "pykeg.web.setup_wizard" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("setup/", include(setup_wizard_urls)),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.KEGBOT_ENABLE_ADMIN:
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]

# main kegweb urls
urlpatterns += [
    path("", include(kegweb_urls)),
]
