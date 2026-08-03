from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from pykeg.api import urls as api_urls
from pykeg.web import spa
from pykeg.web.api import urls as legacy_api_urls

urlpatterns = [
    # The deprecated legacy api is served only at api/v1/; everything else
    # under api/ is the current api.
    path("api/v1/", include(legacy_api_urls)),
    path("api/", include(api_urls)),
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

# Named SPA routes: these exist so server-side code that builds URLs
# (get_absolute_url, e-mail links) keeps working; the SPA handles the
# actual routing client-side.
urlpatterns += [
    path("", spa.spa_index, name="kb-home"),
    path("kegs/<int:keg_id>/", spa.spa_index, name="kb-keg"),
    path("drinks/<int:drink_id>/", spa.spa_index, name="kb-drink"),
    path("d/<int:drink_id>/", spa.spa_index, name="kb-drink-short"),
    path("s/<int:session_id>/", spa.spa_index, name="kb-session-short"),
    path(
        "sessions/<int:year>/<int:month>/<int:day>/<int:pk>/",
        spa.spa_index,
        name="kb-session-detail",
    ),
    path("drinkers/<str:username>/", spa.spa_index, name="kb-drinker"),
    path("account/", spa.spa_index, name="kb-account-main"),
    path("account/confirm-email/<str:token>", spa.spa_index, name="account-confirm-email"),
    path("account/activate/<str:activation_key>/", spa.spa_index, name="activate-account"),
    path("accounts/register/", spa.spa_index, name="registration_register"),
    path(
        "accounts/password/reset/confirm/<str:uidb64>-<str:token>/",
        spa.spa_index,
        name="password_reset_confirm",
    ),
]

# Everything else (except API, asset, and admin paths, whose 404s stay
# real 404s) is SPA territory.
urlpatterns += [
    re_path(r"^(?!api(?:$|/)|media/|static/|admin(?:$|/)).*$", spa.spa_index, name="spa-index"),
]
