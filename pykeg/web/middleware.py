import logging

from django.db import connection
from django.http import JsonResponse
from django.utils import timezone

from pykeg.core import models
from pykeg.core.util import get_version_object, must_upgrade, set_current_request
from pykeg.plugin import util as plugin_util
from pykeg.util import dbstatus
from pykeg.web.api.util import is_api_v1_request

logger = logging.getLogger(__name__)


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
    """Rewrites `request.path` to ignore trailing slashes for legacy api requests.

    Earlier versions of kegbot-server tolerated an optional trailing slash.
    We don't want to define every API url as an `re_path(r".../?")`.

    Rewrite `request.{path,path_info}` so that onward request handling always
    sees a path as if the client presented no trailing slash.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/v1") and not getattr(request, "path_rewritten", None):
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

        # On a fresh install the session table doesn't exist yet, so a
        # real session read/write would crash; stub it out for the setup
        # api until migrations (run in the first setup step) create the
        # table. Once it exists, keep the real session so setup can log
        # the new admin in.
        if request.path.startswith("/api/setup"):
            if "django_session" not in connection.introspection.table_names():
                request.session = {}
                request.session["_auth_user_backend"] = None

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
        """Gates API requests while setup/upgrade is required.

        Only API paths are intercepted (with a JSON 403 the frontend
        understands); everything else falls through to the SPA shell,
        which reads the same signal from its boot request and renders
        the setup flow.
        """
        if is_api_v1_request(request):
            # The legacy API handles "setup required" differently.
            return None

        if request.path.startswith("/api/setup"):
            # The setup API is how the frontend performs setup/upgrade.
            return None

        if request.path.startswith("/api/kegboard-event"):
            # The kegboard endpoint answers setup mode itself (503, so
            # devices keep events queued instead of dropping the batch).
            return None

        if not request.path.startswith("/api/"):
            return None

        if request.need_setup:
            return JsonResponse({"error": "setup_required"}, status=403)
        elif request.need_upgrade:
            return JsonResponse(
                {
                    "error": "upgrade_required",
                    "installed_version": getattr(request, "installed_version_string", None),
                },
                status=403,
            )

        return None


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
