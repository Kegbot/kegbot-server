from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from pykeg.api import urls as api_urls
from pykeg.web.account import urls as account_urls
from pykeg.web.api import urls as legacy_api_urls
from pykeg.web.kbregistration import urls as kbregistration_urls
from pykeg.web.kegadmin import urls as kegadmin_urls
from pykeg.web.kegweb import urls as kegweb_urls
from pykeg.web.setup_wizard import urls as setup_wizard_urls

urlpatterns = [
    # The deprecated legacy api is served only at api/v1/; everything else
    # under api/ is the current api.
    path("api/v1/", include(legacy_api_urls)),
    path("api/", include(api_urls)),
    path("account/", include(account_urls)),
    path("accounts/", include(kbregistration_urls)),
    path("kegadmin/", include(kegadmin_urls)),
]

if "pykeg.web.setup_wizard" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("setup/", include(setup_wizard_urls)),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media uploads in all environments.
urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)

if settings.KEGBOT_ENABLE_ADMIN:
    urlpatterns += [
        path("admin/rq/", include("django_rq.urls")),
        path("admin/", admin.site.urls),
    ]

# main kegweb urls
urlpatterns += [
    path("", include(kegweb_urls)),
]
