import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from pykeg import config
from pykeg.core import models
from pykeg.core.util import get_version_object, must_upgrade, set_current_request
from pykeg.plugin import util as plugin_util
from pykeg.util import dbstatus
from pykeg.web.api.util import is_api_v1_request

logger = logging.getLogger(__name__)

# Requests are always allowed for these path prefixes.
PRIVACY_EXEMPT_PATHS = (
    "/account/activate",
    "/accounts/",
    "/admin/",
    "/media/",
    "/setup/",
    "/sso/login",
    "/sso/logout",
    # Enforced by v2 api auth layer
    "/api/v2",
)

PRIVACY_EXEMPT_PATHS += getattr(settings, "KEGBOT_EXTRA_PRIVACY_EXEMPT_PATHS", ())


def _path_allowed(path, kbsite):
    for p in PRIVACY_EXEMPT_PATHS:
        if path.startswith(p):
            return True
    return False


class CurrentRequestMiddleware:
    """Set/clear the current request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        try:
            response = self.get_response(request)
        finally:
            set_current_request(None)
        return response


class ErrorLoggingMiddleware:
    """Log uncaught exceptions to python logging."""

    logger = logging.getLogger(__name__)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except:
            self.logger.exception("Server error")
            raise


class PathRewriteMiddleware:
    """Rewrites `request.path` to ignore trailing slashes for /api/ requests.

    Earlier versions of kegbot-server tolerated an optional trailing slash.
    We don't want to define every API url as an `re_path(r".../?")`.

    Rewrite `request.{path,path_info}` so that onward request handling always
    sees a path as if the client presented no trailing slash.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api") and not getattr(request, "path_rewritten", None):
            if not request.path.startswith("/api/v2"):
                if request.path.endswith("/"):
                    request.path = request.path[:-1]
                    request.path_info = request.path_info[:-1]
                    request.path_rewritten = True
        return self.get_response(request)


class IsSetupMiddleware:
    """Adds `.need_setup`, `.need_upgrade`, and `.kbsite` to the request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.need_setup = False
        request.need_upgrade = False
        request.kbsite = None

        # Skip all checks if we're in the setup wizard.
        if request.path.startswith("/setup"):
            request.session = {}
            request.session["_auth_user_backend"] = None
            return self.get_response(request)

        # First confirm the database is working.
        try:
            dbstatus.check_db_status()
        except dbstatus.DatabaseNotInitialized:
            logger.warning("Database is not initialized, sending to setup ...")
            request.need_setup = True
            request.need_upgrade = True
        except dbstatus.NeedMigration:
            logger.warning("Database needs migration, sending to setup ...")
            request.need_upgrade = True

        # If the database looks good, check the data.
        if not request.need_setup:
            installed_version = models.KegbotSite.get_installed_version()
            if installed_version is None:
                logger.warning("Kegbot not installed, sending to setup ...")
                request.need_setup = True
            else:
                request.installed_version_string = str(installed_version)
                if must_upgrade(installed_version, get_version_object()):
                    logger.warning("Kegbot upgrade required, sending to setup ...")
                    request.need_upgrade = True

        # Lastly verify the kbsite record.
        if not request.need_setup:
            request.kbsite = models.KegbotSite.objects.get(name="default")
            if not request.kbsite.is_setup:
                logger.warning("Setup incomplete, sending to setup ...")
                request.need_setup = True

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if is_api_v1_request(request):
            # API endpoints handle "setup required" differently.
            return None

        if request.need_setup:
            return self._setup_required(request)
        elif request.need_upgrade:
            return self._upgrade_required(request)

        return None

    def _setup_required(self, request):
        return render(request, "setup_wizard/setup_required.html", status=403)

    def _upgrade_required(self, request):
        context = {
            "installed_version": getattr(request, "installed_version_string", None),
        }
        return render(request, "setup_wizard/upgrade_required.html", context=context, status=403)


class KegbotSiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.kbsite and not request.need_setup:
            timezone.activate(request.kbsite.timezone)
            request.plugins = dict(
                (p.get_short_name(), p) for p in list(plugin_util.get_plugins().values())
            )

        return self.get_response(request)


class PrivacyMiddleware:
    """Enforces site privacy settings.

    Must be installed after ApiRequestMiddleware (in request order) to
    access is_api_v1_request attribute.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not hasattr(request, "kbsite"):
            return None
        elif _path_allowed(request.path, request.kbsite):
            return None
        elif request.is_api_v1_request:
            # api.middleware will enforce access requirements.
            return None

        privacy = request.kbsite.privacy

        if privacy == "public":
            return None
        elif privacy == "staff":
            if not request.user.is_staff:
                return render(request, "kegweb/staff_only.html", status=401)
            return None
        elif privacy == "members":
            if not request.user.is_authenticated or not request.user.is_active:
                return render(request, "kegweb/members_only.html", status=401)
            return None

        return HttpResponse(
            "Server misconfigured, unknown privacy setting:%s" % privacy, status=500
        )
