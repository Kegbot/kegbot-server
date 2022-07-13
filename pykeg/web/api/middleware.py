import logging
from builtins import object

from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers

from . import util

LOGGER = logging.getLogger(__name__)

# These paths are allowed without authorization, regardless of
# site privacy settings.
WHITELISTED_API_PATHS = (
    "/api/devices/link",
    "/api/v1/devices/link",
    "/api/login",
    "/api/v1/login",
    "/api/version",
    "/api/v1/version",
    "/api/get-api-key",
    "/api/v1/get-api-key",
)

WHITELISTED_API_PATHS += getattr(settings, "KEGBOT_EXTRA_WHITELISTED_API_PATHS", ())


class ApiRequestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if util.is_api_request(request):
            if not isinstance(response, HttpResponse):
                data = util.prepare_data(response)
                data["meta"] = {"result": "ok"}
                response = util.build_response(request, data, 200)

            add_never_cache_headers(response)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.is_kb_api_request = util.is_api_request(request)
        if not request.is_kb_api_request:
            # Not an API request. Skip me.
            return None

        try:
            if request.need_setup:
                raise ValueError("Setup required")
            elif request.need_upgrade:
                raise ValueError("Upgrade required")

            need_auth = util.needs_auth(view_func)
            privacy = request.kbsite.privacy
            if request.path.startswith(WHITELISTED_API_PATHS):
                # API request to whitelisted path.
                need_auth = False
            else:
                # API request to non-whitelisted path, in non-public site privacy mode.
                # Demand API key.
                if privacy == "members" and not request.user.is_authenticated:
                    need_auth = True
                elif privacy == "staff" and not request.user.is_staff:
                    need_auth = True

            if need_auth:
                util.check_api_key(request)

            return None

        except Exception as e:
            return util.wrap_exception(request, e)

    def process_exception(self, request, exception):
        """Wraps exceptions for API requests."""
        if util.is_api_request(request):
            return util.wrap_exception(request, exception)
        return None


def cache_key(request):
    return "api:%s" % request.get_full_path()
